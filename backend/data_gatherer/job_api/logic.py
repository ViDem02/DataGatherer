import csv
import os
from queue import Queue
from threading import Thread

from django.core.exceptions import ValidationError
from django.db import connections
from django.db.models import Q
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

    prj_hashtags = Hashtag.objects.filter(
        project=project
    ).order_by('content')
    prj_users = IGUser.objects.filter(
        project=project
    ).order_by('name')

    for hashtag in prj_hashtags:
        uses = UserHashtagUse.objects.filter(
            hashtag=hashtag
        ).count()

        if uses == 0:
            prj_hashtags = prj_hashtags.exclude(pk=hashtag.pk)

    for user in prj_users:
        uses = UserHashtagUse.objects.filter(
            igUser=user
        ).count()

        if uses == 0:
            prj_users = prj_users.exclude(pk=user.pk)

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
                )

                job_users = JobIGUser.objects.filter(job=job)
                with tqdm(total=queryset.count(), desc="Creating associations", unit="user", leave=False) as pbar2:
                    for j_item in queryset:
                        uhu: UserHashtagUse = j_item
                        JobUserHashtagUse.objects.create(
                            job=job,
                            user=job_users.get(name=uhu.igUser.name),
                            hashtag=job_hashtag,
                            image_path=uhu.image.file.path
                        )
                        pbar2.update(1)

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

    ig_users = JobIGUser.objects.filter(job=job).order_by('name')
    hashtags = JobHashtag.objects.filter(task=task).order_by('content')

    data = [[""] + list(ig_users.values_list('name', flat=True))]

    counter = 0
    for hashtag in hashtags:
        j_hashtag: JobHashtag = hashtag
        row = [j_hashtag.content]
        for user in ig_users:
            j_user: JobIGUser = user
            row.append(JobUserHashtagUse.objects.filter(
                user=j_user,
                hashtag=j_hashtag,
                job=job,
            ).count())
        data.append(row)
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

    task.inProgress = False
    task.isCompleted = True
    task.save()

    for conn in connections.all():
        conn.close()


def do_chunks(chunks, job):
    from job_api.models import Task, Job
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
    job.isWorking = False
    job.isCompleted = True
    job.save()
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
