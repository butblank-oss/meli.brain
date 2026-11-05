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

// 기존 판과 같은 네모 체크 (9px 라운드 · 미체크는 빈 네모 · 34/32px)
function Box({ on, big }: { on: boolean; big?: boolean }) {
  return <i className={`bx${on ? ' on' : ''}${big ? ' big' : ''}`} aria-hidden>{on ? '✓' : ''}</i>
}

function Err({ show, children, id }: { show: boolean; children: string; id: string }) {
  return (
    <Collapse open={show}>
      <p className="err" id={id} role="alert">{children}</p>
    </Collapse>
  )
}

const fmt = (d: string) =>
  d.length <= 3 ? d : d.length <= 7 ? `${d.slice(0, 3)}-${d.slice(3)}` : `${d.slice(0, 3)}-${d.slice(3, 7)}-${d.slice(7, 11)}`

const Q = new URLSearchParams(location.search)
const BARE = Q.has('bare')
const LOOK = ['a','b','c','d','e'].includes(Q.get('look') || '') ? Q.get('look')! : 'a'
// a 정리안 · b 카드형 · c 종이 안내문 · d 큰 색면 · e 초록 안심

export default function App() {
  const [tel, setTel] = useState('')
  const [status, setStatus] = useState<Status>('idle')
  const [name, setName] = useState('')
  const [dong, setDong] = useState('')
  const [agree, setAgree] = useState({ a: false, b: false, c: false })
  const [sheet, setSheet] = useState(false)
  const [toast, setToast] = useState('')
  const [tried, setTried] = useState(false)
  const [age, setAge] = useState<'' | 'yes' | 'no'>('')
  const timer = useRef<number>()

  // 번호가 다 적히면 조회한다. 번호가 바뀌면 조회 결과와 잠금은 처음으로 돌아간다 (불변식 1)
  useEffect(() => {
    window.clearTimeout(timer.current)
    if (tel.length < 11) { setStatus('idle'); setName(''); setDong(''); setAge(''); setAgree({ a: false, b: false, c: false }); return }
    setStatus('checking')
    timer.current = window.setTimeout(() => setStatus(tel === '01012345678' ? 'exists' : 'new'), 700)
    return () => window.clearTimeout(timer.current)
  }, [tel])

  useEffect(() => {
    if (!toast) return
    const t = window.setTimeout(() => setToast(''), 3200)
    return () => window.clearTimeout(t)
  }, [toast])

  const open = status === 'new'
  const all = agree.a && agree.b && agree.c
  const left = [
    tel.length < 11 && '휴대전화 번호',
    !name.trim() && '이름',
    !dong && '사시는 곳',
    age !== 'yes' && '나이 확인',
    !all && '동의',
  ].filter(Boolean) as string[]

  const submit = () => {
    setTried(true)
    if (status === 'exists') return setToast('이미 신청하신 번호예요. 다른 번호로 해보세요.')
    if (age === 'no') return setToast('만 60세 이상이신 분만 신청할 수 있어요.')
    if (!left.length) return setToast('여기까지 확인했습니다. 접수 완료 화면은 다음 단계에서 붙입니다.')
    // 빠진 칸이 있으면 알리고 끝내지 않고, 첫 번째 빠진 칸으로 데려간다
    const first = tel.length < 11 ? 'e-tel' : !name.trim() ? 'e-name' : !dong ? 'e-dong' : age !== 'yes' ? 'e-age' : 'e-agree'
    window.setTimeout(() => {
      document.getElementById(first)?.scrollIntoView({ block: 'center', behavior: 'smooth' })
    }, 60)
  }

  const toggleAll = () => {
    const on = !all
    setAgree({ a: on, b: on, c: on })
  }

  return (
    <div className={`pg${BARE ? ' bare' : ''}`}>
      <header className="pg-head">
        <span className="pg-chip">맬리브레인 신청폼 v2 · 눌러보는 판</span>
        <h1>두뇌운동 치매예방교실 4기 참가 신청</h1>
        <p>
          실제로 눌러집니다. 번호를 11자리 적으면 아래 칸이 열립니다.
          <b> 010-1234-5678</b> 로 적으면 이미 신청한 경우를 볼 수 있습니다.
          접수 완료 화면과 약관 전문은 다음 단계입니다.
        </p>
      </header>

      <Phone width={392} className="pg-phone">
        <div className={`sc look-${LOOK}`}>
          <div className="sc-scroll">
            <div className="sc-brand">매일 이롭게, 맬리브레인</div>
            <div className="sc-top">
              <span className="sc-org">인천 남동구 보건소</span>
              <div className="sc-h1">치매예방교실 4기<br />참가 신청</div>
              <div className="sc-sub">인천 남동구에 사시는 분만 신청할 수 있어요.<br />보건소에서 확인한 뒤 이용하실 수 있습니다.</div>
            </div>

            <div className="sc-body">
              <section>
                <div className="lb">휴대전화 번호 <i className="need">꼭 적어주세요</i></div>
                <div className="help">앱에 들어갈 때 쓰는 번호입니다. 번호만 있으면 들어갈 수 있어요.</div>
                <label className={`inp${tel ? ' on' : ''}`}>
                  <input
                    inputMode="numeric"
                    value={fmt(tel)}
                    placeholder="010-0000-0000"
                    aria-label="휴대전화 번호"
                    aria-describedby="e-tel"
                    onChange={(e) => setTel(e.target.value.replace(/\D/g, '').slice(0, 11))}
                  />
                  {status === 'checking' && <Spinner size={22} />}
                </label>
                <Collapse open={status === 'new'}>
                  <div className="note ok"><Box on /> 처음 오셨네요. 아래 항목만 적어주시면 됩니다.</div>
                </Collapse>
                <p className="safe">적어주신 번호는 <b>보건소 확인과 안내 문자</b>에만 씁니다. 다른 곳에 알리지 않습니다.</p>
                <button className="ask" onClick={() => setToast('번호를 모르시면 보건소 032-453-6160 으로 전화 주세요. 직원이 도와드립니다.')}>
                  번호를 잘 모르시겠어요?
                </button>
                <Err show={tried && tel.length < 11} id="e-tel">번호를 11자리 다 적어주세요</Err>
                <Collapse open={status === 'exists'}>
                  <div className="note warn">이미 이 번호로 신청하셨어요. 보건소 <b>032-453-6160</b> 으로 물어보시면 됩니다.</div>
                </Collapse>
              </section>

              <section>
                <div className="lb">이름 <i className="need">꼭 적어주세요</i></div>
                {open ? (
                  <label className={`inp${name ? ' on' : ''}`}>
                    <input value={name} placeholder="예) 홍길동" aria-label="이름" aria-describedby="e-name" onChange={(e) => setName(e.target.value.slice(0, 20))} />
                  </label>
                ) : (
                  <div className="lock">번호를 먼저 적어주세요</div>
                )}
                <Err show={tried && open && !name.trim()} id="e-name">이름을 적어주세요</Err>
              </section>

              <section>
                <div className="lb">사시는 곳 <i className="need">꼭 골라주세요</i></div>
                <div className="help">인천 남동구 보건소에서 운영하는 교실이라 인천 남동구에 사시는 분만 신청할 수 있어요.</div>
                <div className="fixed"><span>인천광역시 남동구</span><span className="dim">고정</span></div>
                {open ? (
                  <button className={`pick${dong ? ' on' : ''}`} onClick={() => setSheet(true)}>
                    <span>{dong || '동을 골라주세요'}</span><span className="arr">›</span>
                  </button>
                ) : (
                  <div className="lock">번호를 먼저 적어주세요</div>
                )}
                <Err show={tried && open && !dong} id="e-dong">사시는 동을 골라주세요</Err>
              </section>

              <section>
                <div className="lb">나이 확인 <i className="need">꼭 골라주세요</i></div>
                <div className="help">이 교실은 <b>만 60세 이상</b> 어르신을 위한 수업이에요.</div>
                {open ? (
                  <>
                    <div className="pickrow">
                      <button className={`opt${age === 'yes' ? ' on' : ''}`} onClick={() => setAge('yes')}>
                        <Box on={age === 'yes'} /> 만 60세 이상이에요
                      </button>
                      <button className={`opt${age === 'no' ? ' on' : ''}`} onClick={() => setAge('no')}>
                        <Box on={age === 'no'} /> 아직 60세가 안 됐어요
                      </button>
                    </div>
                    <Collapse open={age === 'no'}>
                      <div className="note warn">
                        이 교실은 만 60세 이상이신 분만 신청할 수 있어요.<br />
                        보건소 <b>032-453-6160</b> 으로 물어보시면 다른 교실을 알려드립니다.
                      </div>
                    </Collapse>
                  </>
                ) : (
                  <div className="lock">번호를 먼저 적어주세요</div>
                )}
                <Err show={tried && open && age !== 'yes'} id="e-age">나이를 골라주세요</Err>
              </section>

              <section>
                <div className="lb">동의해 주세요 <i className="need">세 가지 모두</i></div>
                {open ? (
                  <>
                    <button className="agr all" onClick={toggleAll}>
                      <Box on={all} big />
                      <span>
                        아래 내용에 모두 동의합니다
                        <i>세 가지 모두 동의하셔야 신청할 수 있어요</i>
                      </span>
                    </button>
                    {AGREES.map((a) => (
                      <button key={a.k} className="agr" onClick={() => setAgree((p) => ({ ...p, [a.k]: !p[a.k] }))}>
                        <Box on={agree[a.k]} />
                        <span>[필수] {a.t}</span>
                        <i className="view" onClick={(e) => { e.stopPropagation(); setToast('약관 전문은 다음 단계에서 붙입니다.') }}>보기</i>
                      </button>
                    ))}
                  </>
                ) : (
                  <div className="lock">번호를 먼저 적어주세요</div>
                )}
                <Err show={tried && open && !all} id="e-agree">세 가지 모두 눌러주세요</Err>
              </section>
            </div>
          </div>

          <div className="sc-cta">
            <div className="rest">{left.length ? `아직 남은 것: ${left.join(' · ')}` : '다 적으셨어요. 신청하기를 눌러주세요.'}</div>
            <button className="btn" onClick={submit}>신청하기</button>
          </div>

          {/* 거주 동 고르기 */}
          <div className={`sh${sheet ? ' open' : ''}`} onClick={() => setSheet(false)}>
            <div className="sh-box" onClick={(e) => e.stopPropagation()}>
              <div className="sh-head">
                <b>어느 동에 사시나요?</b>
                <button className="sh-x" onClick={() => setSheet(false)}>닫기</button>
              </div>
              <div className="sh-list">
                {DONGS.map((d) => (
                  <button key={d} className={`sh-i${dong === d ? ' on' : ''}`} onClick={() => { setDong(d); setSheet(false) }}>{d}</button>
                ))}
              </div>
              <div className="sh-out">
                <button onClick={() => { setSheet(false); setToast('잘 모르시면 보건소 032-453-6160 으로 물어보세요.') }}>잘 모르겠어요 · 도와주세요</button>
                <button onClick={() => { setSheet(false); setToast('남동구에 안 사시면 이 교실은 신청할 수 없어요. 앱은 그냥 쓰실 수 있습니다.') }}>인천 남동구에 살지 않아요</button>
              </div>
            </div>
          </div>

          <div className={`tt${toast ? ' on' : ''}`}>{toast}</div>
        </div>
      </Phone>
    </div>
  )
}
