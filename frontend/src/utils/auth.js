const AUTH_KEY = 'zyxt_db_auth'

export function saveAuth(payload) {
  localStorage.setItem(AUTH_KEY, JSON.stringify(payload))
}

export function getAuth() {
  const raw = localStorage.getItem(AUTH_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

export function isLoggedIn() {
  const auth = getAuth()
  return Boolean(auth?.username)
}

export function clearAuth() {
  localStorage.removeItem(AUTH_KEY)
}
