import React, { useState } from 'react';

const App: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({ username: '', password: '' });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    alert(isLogin ? `Вход: ${formData.username}` : `Регистрация: ${formData.username}`);
  };

  return (
    <div style={styles.container}>
      <div style={styles.authBox}>
        <h2 style={styles.title}>{isLogin ? 'Вход' : 'Регистрация'}</h2>

        <form onSubmit={handleSubmit} style={styles.form}>
          <input
            type="text"
            placeholder="Логин"
            value={formData.username}
            onChange={(e) => setFormData({...formData, username: e.target.value})}
            style={styles.input}
          />
          <input
            type="password"
            placeholder="Пароль"
            value={formData.password}
            onChange={(e) => setFormData({...formData, password: e.target.value})}
            style={styles.input}
          />
          <button type="submit" style={styles.button}>
            {isLogin ? 'Войти' : 'Зарегистрироваться'}
          </button>
        </form>

        <button onClick={() => setIsLogin(!isLogin)} style={styles.switchButton}>
          {isLogin ? 'Нет аккаунта?' : 'Уже есть аккаунт?'}
        </button>
      </div>
    </div>
  );
};

const styles = {
  container: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '100vh',
    backgroundColor: '#7E7E7E',
    padding: '20px',
  },
  authBox: {
    backgroundColor: '#FFFFFF',
    padding: '40px',
    borderRadius: '60px',
    width: '100%',
    maxWidth: '400px',
  },
  title: {
    textAlign: 'center' as const,
    marginBottom: '30px',
    color: '#333',
  },
  form: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '20px',
  },
  input: {
    padding: '15px',
    borderRadius: '60px',
    border: '2px solid #7E7E7E',
    fontSize: '16px',
  },
  button: {
    padding: '15px',
    borderRadius: '60px',
    backgroundColor: '#7E7E7E',
    color: 'white',
    border: 'none',
    fontSize: '16px',
    cursor: 'pointer',
  },
  switchButton: {
    marginTop: '20px',
    backgroundColor: 'transparent',
    border: 'none',
    color: '#7E7E7E',
    cursor: 'pointer',
    textDecoration: 'underline' as const,
  },
};

export default App;