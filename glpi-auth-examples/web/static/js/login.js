const state = {
  csrf: null,
};

function sanitize(str) {
  if (!str) return "";
  return str.replace(/[<>]/g, "").trim();
}

async function getCSRF() {
  const r = await fetch('/csrf');
  const j = await r.json();
  state.csrf = j.token;
}

async function prefill() {
  try {
    const r = await fetch('/prefill');
    const j = await r.json();
    const loginEl = document.getElementById('login');
    if (j.username && !loginEl.value) loginEl.value = j.username;
  } catch {}
}

function validateLogin() {
  const login = document.getElementById('login').value;
  const err = document.getElementById('loginError');
  if (!login) {
    err.textContent = 'Usuário é obrigatório';
    return false;
  }
  err.textContent = '';
  return true;
}

function validatePassword() {
  const pwd = document.getElementById('password').value;
  const err = document.getElementById('passwordError');
  if (!pwd) {
    err.textContent = 'Senha é obrigatória';
    return false;
  }
  if (pwd.length < 8) {
    err.textContent = 'Senha deve ter no mínimo 8 caracteres';
    return false;
  }
  err.textContent = '';
  return true;
}

async function submitLogin(e) {
  e.preventDefault();
  const serverErr = document.getElementById('serverError');
  const success = document.getElementById('success');
  serverErr.textContent = '';
  success.textContent = '';
  const ok = validateLogin() & validatePassword();
  if (!ok) return;
  const login = sanitize(document.getElementById('login').value);
  const password = sanitize(document.getElementById('password').value);
  try {
    const r = await fetch('/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': state.csrf || ''
      },
      body: JSON.stringify({ login, password })
    });
    const j = await r.json();
    if (!j.ok) {
      if (j.errors) {
        document.getElementById('loginError').textContent = j.errors.login || '';
        document.getElementById('passwordError').textContent = j.errors.password || '';
      } else {
        serverErr.textContent = j.error || 'Falha na autenticação';
      }
      return;
    }
    success.textContent = `Autenticado como ${j.user || login}. Sessão: ${j.session_token_prefix}...`;
  } catch (err) {
    serverErr.textContent = 'Erro de rede';
  }
}

function togglePassword() {
  const btn = document.getElementById('togglePwd');
  const pwd = document.getElementById('password');
  const show = pwd.type === 'password';
  pwd.type = show ? 'text' : 'password';
  btn.textContent = show ? 'Ocultar' : 'Mostrar';
  btn.setAttribute('aria-pressed', show ? 'true' : 'false');
}

window.addEventListener('DOMContentLoaded', async () => {
  await getCSRF();
  await prefill();
  document.getElementById('login').addEventListener('input', validateLogin);
  document.getElementById('password').addEventListener('input', validatePassword);
  document.getElementById('loginForm').addEventListener('submit', submitLogin);
  document.getElementById('togglePwd').addEventListener('click', togglePassword);
});

