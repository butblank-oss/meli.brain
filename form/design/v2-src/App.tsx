import { useEffect, useRef, useState } from 'react'
import { Phone, Spinner, Collapse } from './kit'

const DONGS = ['구월1동','구월2동','구월3동','구월4동','간석1동','간석2동','간석3동','간석4동',
  '만수1동','만수2동','만수3동','만수4동','만수5동','만수6동','남촌도림동','논현1동','논현2동',
  '논현고잔동','장수서창동','서창2동']

const AGREES = [
  { k: 'a', t: '맬리브레인 서비스 이용약관' },
  { k: 'b', t: '개인정보 수집·이용 동의' },
  { k: 'c', t: '남동구 보건소에 참여 정보 제공 동의' },
] as const

type Status = 'idle' | 'checking' | 'new' | 'exists'

const Q = new URLSearchParams(location.search)
const BARE = Q.has('bare')
const LOOK = ['a','b','c','d','e','p4'].includes(Q.get('look') || '') ? Q.get('look')! : 'a'
const FLOW = Q.has('flow')   // 순차 공개 — 지금 여쭙는 것만 펼친다

function Box({ on, big }: { on: boolean; big?: boolean }) {
  return <i className={`bx${on ? ' on' : ''}${big ? ' big' : ''}`} aria-hidden>{on ? '✓' : ''}</i>
}

const fmt = (d: string) =>
  d.length <= 3 ? d : d.length <= 7 ? `${d.slice(0, 3)}-${d.slice(3)}` : `${d.slice(0, 3)}-${d.slice(3, 7)}-${d.slice(7, 11)}`

export default function App() {
  const [tel, setTel] = useState('')
  const [status, setStatus] = useState<Status>('idle')
  const [name, setName] = useState('')
  const [dong, setDong] = useState('')
  const [age, setAge] = useState<'' | 'yes' | 'no'>('')
  const [agree, setAgree] = useState({ a: false, b: false, c: false })
  const [sheet, setSheet] = useState(false)
  const [toast, setToast] = useState('')
  const [tried, setTried] = useState(false)
  const [back, setBack] = useState<number | null>(null)   // 고치려고 되돌아간 단계
  const timer = useRef<number>()

  useEffect(() => {
    window.clearTimeout(timer.current)
    if (tel.length < 11) { setStatus('idle'); setName(''); setDong(''); setAge(''); setAgree({ a: false, b: false, c: false }); return }
    setStatus('checking')
    timer.current = window.setTimeout(() => setStatus(tel === '01012345678' ? 'exists' : 'new'), 700)
    return () => window.clearTimeout(timer.current)
  }, [tel])

  useEffect(() => {
    if (!toast) return
    const t = window.setTimeout(() => setToast(''), 3400)
    return () => window.clearTimeout(t)
  }, [toast])

  const open = status === 'new'
  const all = agree.a && agree.b && agree.c

  // 다섯 가지를 순서대로 여쭙는다
  const steps = [
    { k: 'tel',   short: '휴대폰 번호', ask: '휴대폰 번호를\n알려주세요',  done: tel.length === 11 && open, value: fmt(tel) },
    { k: 'name',  short: '성함',        ask: '성함이\n어떻게 되세요?',     done: !!name.trim(),             value: name },
    { k: 'dong',  short: '사시는 동',   ask: '어디에\n사세요?',            done: !!dong,                    value: dong },
    { k: 'age',   short: '연세',        ask: '연세가\n어떻게 되세요?',     done: age === 'yes',             value: '만 60세 이상' },
    { k: 'agree', short: '동의',        ask: '마지막이에요',               done: all,                       value: '세 가지 모두 동의' },
  ]
  const firstTodo = steps.findIndex((s) => !s.done)
  const cur = back !== null ? back : firstTodo === -1 ? steps.length : firstTodo
  const show = (i: number) => !FLOW || i === cur || steps[i].done
  const live = (i: number) => !FLOW || i === cur

  const left = steps.filter((s) => !s.done).map((s) => s.short)

  const submit = () => {
    setTried(true)
    if (status === 'exists') return setToast('이 번호로는 이미 신청하셨어요.')
    if (age === 'no') return setToast('만 60세가 넘으신 분만 신청하실 수 있어요.')
    if (!left.length) return setToast('여기까지 확인했어요. 접수 완료 화면은 다음 단계에 붙일게요.')
    setBack(null)
    window.setTimeout(() => document.getElementById(`e-${steps[firstTodo].k}`)?.scrollIntoView({ block: 'center', behavior: 'smooth' }), 60)
  }

  const toggleAll = () => { const on = !all; setAgree({ a: on, b: on, c: on }) }

  // 끝난 항목 한 줄
  const Done = ({ i }: { i: number }) => (
    <div className="row-done">
      <span className="rd-k">{steps[i].short}</span>
      <span className="rd-v">{steps[i].value}</span>
      <button className="rd-fix" onClick={() => setBack(i)}>고치기</button>
    </div>
  )

  const Ask = ({ i }: { i: number }) =>
    <h2 className="ask-h">{steps[i].ask.split('\n').map((l, n) => <span key={n}>{l}<br /></span>)}</h2>

  const Err = ({ show: on, children, id }: { show: boolean; children: string; id: string }) => (
    <Collapse open={on}><p className="err" id={id} role="alert">{children}</p></Collapse>
  )

  return (
    <div className={`pg${BARE ? ' bare' : ''}`}>
      <header className="pg-head">
        <span className="pg-chip">맬리브레인 신청폼 v2 · 눌러보는 판</span>
        <h1>치매예방교실 4기 신청</h1>
        <p>실제로 눌러집니다. 번호를 11자리 적으면 다음을 여쭤봅니다.
          <b> 010-1234-5678</b> 로 적으면 이미 신청한 경우를 볼 수 있습니다.</p>
      </header>

      <Phone width={392} className="pg-phone">
        <div className={`sc look-${LOOK}${FLOW ? ' flow' : ''}`}>
          <div className="sc-scroll">
            <div className="sc-top">
              <span className="sc-org">인천 남동구 보건소</span>
              <div className="sc-h1">치매예방교실 4기<br />신청을 도와드릴게요</div>
              <div className="sc-sub">{FLOW ? '다섯 가지만 여쭤볼게요. 한 번에 하나씩이에요.'
                : '인천 남동구에 사시는 분만 신청하실 수 있어요.'}</div>
            </div>

            <div className="sc-body">
              {/* 1 휴대폰 번호 */}
              {show(0) && (steps[0].done && !live(0) ? <Done i={0} /> : (
                <section>
                  {FLOW ? <Ask i={0} /> : <div className="lb">휴대폰 번호를 알려주세요 <i className="need">꼭 필요해요</i></div>}
                  <div className="help">앱에 들어가실 때 쓰는 번호예요. 번호만 있으면 들어가실 수 있어요.</div>
                  <label className={`inp${tel ? ' on' : ''}`}>
                    <input inputMode="numeric" value={fmt(tel)} placeholder="010-0000-0000"
                      aria-label="휴대폰 번호" aria-describedby="e-tel"
                      onChange={(e) => setTel(e.target.value.replace(/\D/g, '').slice(0, 11))} />
                    {status === 'checking' && <Spinner size={22} />}
                  </label>
                  <Collapse open={status === 'new'}>
                    <div className="note ok"><Box on /> 처음 오셨네요! 아래 것들만 알려주시면 돼요.</div>
                  </Collapse>
                  <Collapse open={status === 'exists'}>
                    <div className="note warn">이 번호로 이미 신청하셨어요. 보건소 <b>032-453-6160</b> 으로 물어보시면 돼요.</div>
                  </Collapse>
                  <p className="safe">알려주신 번호는 보건소 확인과 안내 문자에만 써요. 다른 곳에 알리지 않아요.</p>
                  <button className="ask" onClick={() => setToast('보건소 032-453-6160 으로 전화 주세요. 직원이 도와드릴게요.')}>
                    번호가 기억나지 않으세요?</button>
                  <Err show={tried && tel.length < 11} id="e-tel">번호를 11자리 다 눌러주세요</Err>
                </section>
              ))}

              {/* 2 성함 */}
              {open && show(1) && (steps[1].done && !live(1) ? <Done i={1} /> : (
                <section>
                  {FLOW ? <Ask i={1} /> : <div className="lb">성함이 어떻게 되세요? <i className="need">꼭 필요해요</i></div>}
                  <label className={`inp${name ? ' on' : ''}`}>
                    <input value={name} placeholder="예) 홍길동" aria-label="성함" aria-describedby="e-name"
                      onChange={(e) => setName(e.target.value.slice(0, 20))} />
                  </label>
                  <Err show={tried && !name.trim()} id="e-name">성함을 알려주세요</Err>
                </section>
              ))}

              {/* 3 사시는 동 */}
              {open && show(2) && (steps[2].done && !live(2) ? <Done i={2} /> : (
                <section>
                  {FLOW ? <Ask i={2} /> : <div className="lb">어디에 사세요? <i className="need">꼭 필요해요</i></div>}
                  <div className="help">인천 남동구 보건소에서 여는 교실이라, 남동구에 사시는 분만 신청하실 수 있어요.</div>
                  <div className="fixed"><span>인천광역시 남동구</span><span className="dim">고정</span></div>
                  <button className={`pick${dong ? ' on' : ''}`} onClick={() => setSheet(true)}>
                    <span>{dong || '동을 골라주세요'}</span><span className="arr">›</span>
                  </button>
                  <Err show={tried && !dong} id="e-dong">사시는 동을 골라주세요</Err>
                </section>
              ))}

              {/* 4 연세 */}
              {open && show(3) && (steps[3].done && !live(3) ? <Done i={3} /> : (
                <section>
                  {FLOW ? <Ask i={3} /> : <div className="lb">연세가 어떻게 되세요? <i className="need">꼭 필요해요</i></div>}
                  <div className="help">이 교실은 만 60세 이상 어르신을 위한 수업이에요.</div>
                  <div className="pickrow">
                    <button className={`opt${age === 'yes' ? ' on' : ''}`} onClick={() => setAge('yes')}>
                      <Box on={age === 'yes'} /> 네, 만 60세가 넘었어요</button>
                    <button className={`opt${age === 'no' ? ' on' : ''}`} onClick={() => setAge('no')}>
                      <Box on={age === 'no'} /> 아직 60세가 안 됐어요</button>
                  </div>
                  <Collapse open={age === 'no'}>
                    <div className="note warn">이 교실은 만 60세가 넘으신 분만 신청하실 수 있어요.<br />
                      보건소 <b>032-453-6160</b> 으로 물어보시면 다른 교실을 알려드릴게요.</div>
                  </Collapse>
                  <Err show={tried && age !== 'yes'} id="e-age">연세를 골라주세요</Err>
                </section>
              ))}

              {/* 5 동의 */}
              {open && show(4) && (steps[4].done && !live(4) ? <Done i={4} /> : (
                <section>
                  {FLOW ? <Ask i={4} /> : <div className="lb">마지막이에요 <i className="need">세 가지 모두</i></div>}
                  <button className="agr all" onClick={toggleAll}>
                    <Box on={all} big />
                    <span>세 가지 모두 동의할게요<i>하나씩 눌러서 보셔도 돼요</i></span>
                  </button>
                  {AGREES.map((a) => (
                    <button key={a.k} className="agr" onClick={() => setAgree((p) => ({ ...p, [a.k]: !p[a.k] }))}>
                      <Box on={agree[a.k]} />
                      <span>{a.t}</span>
                      <i className="view" onClick={(e) => { e.stopPropagation(); setToast('약관 전문은 다음 단계에 붙일게요.') }}>보기</i>
                    </button>
                  ))}
                  <Err show={tried && !all} id="e-agree">세 가지 모두 눌러주세요</Err>
                </section>
              ))}
            </div>
          </div>

          <div className="sc-cta">
            <div className="rest">{left.length ? `아직 남은 것이 있어요: ${left.join(' · ')}` : '다 되셨어요. 아래 버튼을 눌러주세요.'}</div>
            <button className="btn" onClick={submit}>신청하기</button>
          </div>

          <div className={`sh${sheet ? ' open' : ''}`} onClick={() => setSheet(false)}>
            <div className="sh-box" onClick={(e) => e.stopPropagation()}>
              <div className="sh-head"><b>어느 동에 사세요?</b>
                <button className="sh-x" onClick={() => setSheet(false)}>닫기</button></div>
              <div className="sh-list">
                {DONGS.map((d) => (
                  <button key={d} className={`sh-i${dong === d ? ' on' : ''}`}
                    onClick={() => { setDong(d); setSheet(false); setBack(null) }}>{d}</button>
                ))}
              </div>
              <div className="sh-out">
                <button onClick={() => { setSheet(false); setToast('보건소 032-453-6160 으로 물어보시면 알려드릴게요.') }}>잘 모르겠어요, 도와주세요</button>
                <button onClick={() => { setSheet(false); setToast('남동구에 안 사시면 이 교실은 어려워요. 앱은 그냥 쓰실 수 있어요.') }}>남동구에 살지 않아요</button>
              </div>
            </div>
          </div>

          <div className={`tt${toast ? ' on' : ''}`}>{toast}</div>
        </div>
      </Phone>
    </div>
  )
}
