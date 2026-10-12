import {useEffect, useState} from "react";
import {keySetSelector} from "../../slices/keyboardSlice";
import {useSelector} from "react-redux";
import {useHotkeys} from "react-hotkeys-hook";
import {useCookies} from "react-cookie";

const HotButton = ({btnRef, children, className, onClick, uniqueHotKeyId, style, disabled}) => {

    const [cookies, setCookies] = useCookies(['keys'])
    const [ignoreCookies, setIgnoreCookies] = useState()


    const reduxKeySetEnabled = useSelector(keySetSelector)
    const [finalClassName, setFinalClassName] = useState(null)
    const [hotkey, setHotkey] = useState(null)
    const [isSetting, setIsSetting] = useState(false)

    useHotkeys('*', (event) => {
        if (event.key === 'Control') return
        if (event.key === ' ') return

        setIgnoreCookies(true)

        if (isSetting) {

            if (event.key === 'Backspace'){
                setIsSetting(false)
                setFinalClassName(`${className} ${
                    reduxKeySetEnabled ? 'btn-warning' : ''
                }`)
                setCookies(uniqueHotKeyId, null)
                setHotkey(null)
                return
            }


            setHotkey(event.key)
            setIsSetting(false)
            setFinalClassName(`${className} ${
                reduxKeySetEnabled ? 'btn-warning' : ''
            }`)
            setCookies(uniqueHotKeyId, event.key)
        }

    })


    useHotkeys(hotkey || "none", (event) => {
        if (reduxKeySetEnabled) return
        if (disabled) return

        setFinalClassName(`${className} btn-warning`)
        setTimeout(() => {
            setFinalClassName(`${className}`)
        }, 100)

        onClick()
    })

    useEffect(() => {
        if (cookies[uniqueHotKeyId] && !ignoreCookies){
            setHotkey(cookies[uniqueHotKeyId])
        }

        if (reduxKeySetEnabled) setFinalClassName(`${className} btn-warning`)
        if (!reduxKeySetEnabled) setFinalClassName(null)

    }, [reduxKeySetEnabled])


    const UniqueShower = () => (
        uniqueHotKeyId && reduxKeySetEnabled ?
            <div className={'font-monospace'} style={{fontSize: '10px'}}>{uniqueHotKeyId}</div>
            : <></>
    )

    const setHotKeyBehaviour = () => {
        setIsSetting(true)
        setFinalClassName(`${className} ${
            reduxKeySetEnabled ? 'btn-info' : ''
        }`)
    }


    return (
        <div>
            <button
                ref={btnRef}
                style={style}
                className={finalClassName || className}
                onClick={reduxKeySetEnabled ? setHotKeyBehaviour : onClick}
                disabled={disabled}
            >
                <UniqueShower/>
                {children}
                <div className={'font-monospace'}>
                    [{hotkey || ' '}]
                </div>
            </button>
        </div>
    )
}

export default HotButton