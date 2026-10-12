import csv
import os
import traceback
from queue import Queue
from threading import Thread

from django.core.exceptions import ValidationError
from django.db import connections
from django.db.models import Count, Q
from django.db.transaction import atomic
from tqdm import tqdm
from django.core.files import File as DjangoFile
from django.utils.text import get_valid_filename


@atomic
def initiate_job(job):
    from storage_api.models.data_models import UserHashtagUse, IGUser, Hashtag
    from job_api.models import Job, Task, JobIGUser, JobHashtag, JobUserHashtagUse
    job: Job = job
    if job.isInitiated:
        job.isInitiating = False
        job.save()
        return

    project = job.project

    # Only the hashtags and users used at least once (one query each, not one per hashtag or user)
    prj_hashtags = list(Hashtag.objects.filter(
        project=project, userhashtaguse__isnull=False
    ).distinct().order_by('content'))
    prj_users = IGUser.objects.filter(
        project=project, userhashtaguse__isnull=False
    ).distinct().order_by('name')

    create_job_users(job, prj_users)

    n = job.taskGranularity
    chunks = [prj_hashtags[i:i + n] for i in range(0, len(prj_hashtags), n)]
    print(f"There will be {len(chunks)} tasks, granularity: {n}")

    create_job_tasks(chunks, job, project)

    job.isInitiated = True
    job.isInitiating = False
    job.save()
    print(f"completed")


def create_job_tasks(chunks, job, project):
    from storage_api.models.data_models import UserHashtagUse, IGUser, Hashtag
    from job_api.models import Job, Task, JobIGUser, JobHashtag, JobUserHashtagUse

    job_users = {job_user.name: job_user for job_user in JobIGUser.objects.filter(job=job)}

    with tqdm(total=len(chunks), desc="Creating tasks", unit="task") as pbar:
        counter = 1
        for chunk in chunks:
            current_task = Task.objects.create(
                progressiveID=counter,
                inProgress=False,
                isCompleted=False,
                job=job,
                totRows=len(chunk)
            )
            for item in chunk:
                hashtag: Hashtag = item
                job_hashtag = JobHashtag.objects.create(
                    job=job,
                    task=current_task,
                    content=hashtag.content
                )

                queryset = UserHashtagUse.objects.filter(
                    project=project,
                    hashtag=hashtag,
                ).select_related('igUser', 'image')

                JobUserHashtagUse.objects.bulk_create([
                    JobUserHashtagUse(
                        job=job,
                        user=job_users[uhu.igUser.name],
                        hashtag=job_hashtag,
                        image_path=uhu.image.file.path
                    )
                    for uhu in queryset
                ])

            counter = counter + 1
            pbar.update(1)


def create_job_users(job, prj_users):
    from storage_api.models.data_models import UserHashtagUse, IGUser, Hashtag
    from job_api.models import Job, Task, JobIGUser, JobHashtag, JobUserHashtagUse

    with tqdm(total=prj_users.count(), desc="Creating job users", unit="user") as pbar:
        for item in prj_users:
            user: IGUser = item
            JobIGUser.objects.create(
                job=job,
                name=user.name
            )
            pbar.update(1)


def do_task(task):
    from storage_api.models.data_models import UserHashtagUse, IGUser, Hashtag
    from job_api.models import Job, Task, JobIGUser, JobHashtag, JobUserHashtagUse

    task: Task = task
    job: Job = task.job

    if task.isCompleted:
        print(f"Warning! Task {task} already completed")
        return

    try:
        ig_users = list(JobIGUser.objects.filter(job=job).order_by('name'))
        hashtags = JobHashtag.objects.filter(task=task).order_by('content')

        # One GROUP BY for the whole task, instead of one COUNT query per user-hashtag pair
        counts = {
            (row['hashtag_id'], row['user_id']): row['uses']
            for row in JobUserHashtagUse.objects.filter(job=job, hashtag__task=task)
            .values('hashtag_id', 'user_id')
            .annotate(uses=Count('id'))
        }

        data = [[""] + [j_user.name for j_user in ig_users]]

        counter = 0
        for hashtag in hashtags:
            j_hashtag: JobHashtag = hashtag
            data.append([j_hashtag.content] + [counts.get((j_hashtag.pk, j_user.pk), 0) for j_user in ig_users])
            counter = counter + 1
            task.currentRow = counter
            task.save()

        try:
            os.makedirs(f"./jobs_elaborations/job_{job.pk}/")
        except FileExistsError:
            # Defeats race condition when another thread created the path
            pass

        with open(f"./jobs_elaborations/job_{job.pk}/{job.pk}_{task.progressiveID}.csv", "w", newline='') as file:
            writer = csv.writer(file, delimiter=";", quoting=csv.QUOTE_ALL)
            writer.writerows(data)

        with open(f"./jobs_elaborations/job_{job.pk}/{job.pk}_{task.progressiveID}.csv", "r", newline='') as file:
            task.file = DjangoFile(file)
            task.save()

        # Only a task whose file was written is completed
        task.isCompleted = True
    except Exception:
        # The task stays not completed, so the job is not completed and working it again retries this task
        print(f"Task {task} failed:\n{traceback.format_exc()}")
    finally:
        task.inProgress = False
        task.save()
        for conn in connections.all():
            conn.close()


def do_chunks(chunks, job):
    from job_api.models import Task, Job
    try:
        counter = 1
        for chunk in chunks:
            print(f"doing chunk {counter}/{len(chunks)}")
            threads = []
            for task in chunk:
                print(f"starting task {task}")
                task: Task = task
                task.inProgress = True
                task.save()
                thread = Thread(target=do_task, args=[task])
                thread.start()
                threads.append(thread)
            for thread in threads:
                thread.join()
            print(f"chunk {counter} is done.")
            counter = counter + 1
    finally:
        # A job is completed only when every one of its tasks is
        job.isWorking = False
        job.isCompleted = not Task.objects.filter(job=job, isCompleted=False).exists()
        job.save()
        if not job.isCompleted:
            print(f"Job {job} stopped with tasks not completed: work it again to retry them.")
        for conn in connections.all():
            conn.close()


def work_job(job, wait=False):

    from job_api.models import Task, Job
    tasks_to_be_done = Task.objects.filter(Q(job=job) & Q(isCompleted=False)).order_by('progressiveID')

    if job.isInitiated is not True:
        return ValidationError(f"The job {job} is not initiated yet! Aborted whole operation.")

    n = job.threads
    chunks = [tasks_to_be_done[i:i + n] for i in range(0, len(tasks_to_be_done), n)]
    print(chunks)
    print(f"There will be {len(chunks)} tasks done in parallel, threads: {n}")

    job.isWorking = True
    job.save()

    thread = Thread(target=do_chunks, args=[chunks, job])
    thread.start()

    if wait:
        thread.join()



def calculate_whole_file(job):
    from job_api.models import Task, Job
    tasks = Task.objects.filter(Q(job=job)).order_by('progressiveID')
    # The title is free text: it must not be able to point outside the job folder
    whole_file_path = f"./jobs_elaborations/job_{job.pk}/whole_job_{get_valid_filename(job.title)}.csv"
    with open(whole_file_path, "w") as write_file:
        for task in tasks:
            task: Task = task
            with open(f"./jobs_elaborations/job_{job.pk}/{job.pk}_{task.progressiveID}.csv", "r") as read_file:
                if task.progressiveID != 1:
                    next(read_file)
                for line in read_file:
                    write_file.write(line)
    with open(whole_file_path, "r") as read_file:
        job.file = DjangoFile(read_file)
        job.save()
