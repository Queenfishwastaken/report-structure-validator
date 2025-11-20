import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate, Navigate } from 'react-router-dom';

// Типы
interface UserProfile {
  id: number;
  username: string;
  email: string;
  full_name: string;
}

interface Report {
  id: number;
  file: string;
  template: string;
  score: number;
  status: string;
  upload_date: string;
}

interface CheckResult {
  найдено_разделов: string[];
  отсутствуют: string[];
  оценка: number;
  статус: string;
  совпадения_детально: string;
  file?: string;
  template?: string;
  error?: string;
}

// Компонент навигации
// Компонент навигации
const Navbar: React.FC = () => {
  const navigate = useNavigate();
  const token = localStorage.getItem('token');

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div>
        <span className="nav-logo">
          Report Validator
        </span>
      </div>
      <div className="nav-links">
        {token ? (
          <>
            <Link to="/" className="nav-link">Главная</Link>
            <Link to="/profile" className="nav-link">Профиль</Link>
            <button onClick={handleLogout} className="nav-link logout-button">
              Выйти
            </button>
          </>
        ) : (
          <>
            <Link to="/login" className="nav-link">Вход</Link>
            <Link to="/register" className="nav-link">Регистрация</Link>
          </>
        )}
      </div>
    </nav>
  );
};

// Компонент входа
const Login: React.FC = () => {
  const [formData, setFormData] = useState({ username: '', password: '' });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const formDataToSend = new FormData();
      formDataToSend.append('username', formData.username);
      formDataToSend.append('password', formData.password);

      const response = await fetch('/api/вход', {
        method: 'POST',
        body: formDataToSend,
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.token);
        localStorage.setItem('username', data.user);
        navigate('/');
      } else {
        alert('Ошибка входа. Проверьте логин и пароль.');
      }
    } catch (error) {
      alert('Ошибка сети. Попробуйте снова.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="auth-box">
        <h2 className="title">Вход</h2>
        <form onSubmit={handleSubmit} className="form">
          <input
            type="text"
            placeholder="Логин"
            value={formData.username}
            onChange={(e) => setFormData({...formData, username: e.target.value})}
            className="input"
            required
          />
          <input
            type="password"
            placeholder="Пароль"
            value={formData.password}
            onChange={(e) => setFormData({...formData, password: e.target.value})}
            className="input"
            required
          />
          <button type="submit" className="button" disabled={loading}>
            {loading ? 'Вход...' : 'Войти'}
          </button>
        </form>
        <Link to="/register">
          <button className="switch-button">
            Нет аккаунта? Зарегистрироваться
          </button>
        </Link>
      </div>
    </div>
  );
};

// Компонент регистрации
const Register: React.FC = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    email: '',
    full_name: ''
  });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const formDataToSend = new FormData();
      formDataToSend.append('username', formData.username);
      formDataToSend.append('password', formData.password);
      formDataToSend.append('email', formData.email);
      formDataToSend.append('full_name', formData.full_name);

      const response = await fetch('/api/регистрация', {
        method: 'POST',
        body: formDataToSend,
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.token);
        localStorage.setItem('username', data.user);
        navigate('/');
      } else {
        const error = await response.json();
        alert(error.detail || 'Ошибка регистрации');
      }
    } catch (error) {
      alert('Ошибка сети. Попробуйте снова.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="auth-box">
        <h2 className="title">Регистрация</h2>
        <form onSubmit={handleSubmit} className="form">
          <input
            type="text"
            placeholder="Логин"
            value={formData.username}
            onChange={(e) => setFormData({...formData, username: e.target.value})}
            className="input"
            required
          />
          <input
            type="password"
            placeholder="Пароль"
            value={formData.password}
            onChange={(e) => setFormData({...formData, password: e.target.value})}
            className="input"
            required
          />
          <input
            type="email"
            placeholder="Email (необязательно)"
            value={formData.email}
            onChange={(e) => setFormData({...formData, email: e.target.value})}
            className="input"
          />
          <input
            type="text"
            placeholder="Полное имя (необязательно)"
            value={formData.full_name}
            onChange={(e) => setFormData({...formData, full_name: e.target.value})}
            className="input"
          />
          <button type="submit" className="button" disabled={loading}>
            {loading ? 'Регистрация...' : 'Зарегистрироваться'}
          </button>
        </form>
        <Link to="/login">
          <button className="switch-button">
            Уже есть аккаунт? Войти
          </button>
        </Link>
      </div>
    </div>
  );
};

// Компонент главной страницы
// Компонент главной страницы
const Home: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [template, setTemplate] = useState('лабораторная');
  const [result, setResult] = useState<CheckResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [templates, setTemplates] = useState<string[]>(['лабораторная', 'курсовая']);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }
    fetchTemplates();
  }, [navigate]);

  const fetchTemplates = async () => {
    try {
      const response = await fetch('/api/шаблоны');
      if (response.ok) {
        const data = await response.json();
        setTemplates(Object.keys(data.templates));
      }
    } catch (error) {
      console.error('Ошибка загрузки шаблонов:', error);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      alert('Пожалуйста, выберите файл');
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('template', template);

      const token = localStorage.getItem('token');
      if (token) {
        formData.append('token', token);
      }

      const response = await fetch('/api/проверить', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      alert('Ошибка при проверке файла');
    } finally {
      setLoading(false);
    }
  };

  // Функция для проверки наличия раздела
  const isSectionFound = (sectionName: string) => {
    if (!result) return false;

    const sectionLower = sectionName.toLowerCase();
    return result.найдено_разделов.some(found =>
      found.toLowerCase().includes(sectionLower)
    );
  };

  return (
    <div className="main-content">
      <div className="content-left">
        <div className="project-title-box">
          <h1>Проверка структуры учебного отчета</h1>
        </div>

        <div className="upload-section">
          <h2>Загрузите документ для проверки</h2>
          <form onSubmit={handleSubmit} className="form">
            <div>
              <label>Выберите шаблон:</label>
              <select
                value={template}
                onChange={(e) => setTemplate(e.target.value)}
                className="input"
              >
                {templates.map(tpl => (
                  <option key={tpl} value={tpl}>{tpl}</option>
                ))}
              </select>
            </div>

            <input
              type="file"
              accept=".docx"
              onChange={handleFileChange}
              className="input"
            />

            <button type="submit" className="button" disabled={loading}>
              {loading ? 'Проверка...' : 'Проверить структуру'}
            </button>
          </form>
        </div>

        {result && (
          <div className="result-section">
            <h2>Результаты проверки</h2>

            {result.error ? (
              <p className="error">{result.error}</p>
            ) : (
              <>
                <div className={`result-status ${result.оценка >= 80 ? 'success' : result.оценка >= 60 ? 'warning' : 'error'}`}>
                  <h3>Оценка: {result.оценка}% - {result.статус}</h3>
                  <p>{result.совпадения_детально}</p>
                </div>

                {result.найдено_разделов.length > 0 && (
                  <div>
                    <h4>Найдены разделы:</h4>
                    <ul>
                      {result.найдено_разделов.map((section, index) => (
                        <li key={index}>{section}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {result.отсутствуют.length > 0 && (
                  <div>
                    <h4>Отсутствуют разделы:</h4>
                    <ul>
                      {result.отсутствуют.map((section, index) => (
                        <li key={index} className="error">{section}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>

      {/* Боковая панель со структурой */}
      <div className="content-right">
        <div className="structure-section">
          <div className="structure-title">Структура документа</div>
          <div className="structure-list">
            {template === 'лабораторная' && (
              <>
                <div className="structure-item">
                  <div className="section-info">
                    <div className={`status-indicator ${isSectionFound('Титульный лист') ? 'found' : 'missing'}`}>
                      {isSectionFound('Титульный лист') ? '✓' : '✗'}
                    </div>
                    <div className="section-card">
                      <span className="section-name">Титульный лист</span>
                    </div>
                  </div>
                </div>
                <div className="structure-item">
                  <div className="section-info">
                    <div className={`status-indicator ${isSectionFound('Введение') ? 'found' : 'missing'}`}>
                      {isSectionFound('Введение') ? '✓' : '✗'}
                    </div>
                    <div className="section-card">
                      <span className="section-name">Введение</span>
                    </div>
                  </div>
                </div>
                <div className="structure-item">
                  <div className="section-info">
                    <div className={`status-indicator ${isSectionFound('Теория') ? 'found' : 'missing'}`}>
                      {isSectionFound('Теория') ? '✓' : '✗'}
                    </div>
                    <div className="section-card">
                      <span className="section-name">Теория</span>
                    </div>
                  </div>
                </div>
                <div className="structure-item">
                  <div className="section-info">
                    <div className={`status-indicator ${isSectionFound('Практика') ? 'found' : 'missing'}`}>
                      {isSectionFound('Практика') ? '✓' : '✗'}
                    </div>
                    <div className="section-card">
                      <span className="section-name">Практика</span>
                    </div>
                  </div>
                </div>
                <div className="structure-item">
                  <div className="section-info">
                    <div className={`status-indicator ${isSectionFound('Заключение') ? 'found' : 'missing'}`}>
                      {isSectionFound('Заключение') ? '✓' : '✗'}
                    </div>
                    <div className="section-card">
                      <span className="section-name">Заключение</span>
                    </div>
                  </div>
                </div>
                <div className="structure-item">
                  <div className="section-info">
                    <div className={`status-indicator ${isSectionFound('Литература') ? 'found' : 'missing'}`}>
                      {isSectionFound('Литература') ? '✓' : '✗'}
                    </div>
                    <div className="section-card">
                      <span className="section-name">Литература</span>
                    </div>
                  </div>
                </div>
              </>
            )}

            {template === 'курсовая' && (
              <>
                <div className="structure-item">
                  <div className="section-info">
                    <div className={`status-indicator ${isSectionFound('Титульный лист') ? 'found' : 'missing'}`}>
                      {isSectionFound('Титульный лист') ? '✓' : '✗'}
                    </div>
                    <div className="section-card">
                      <span className="section-name">Титульный лист</span>
                    </div>
                  </div>
                </div>
                <div className="structure-item">
                  <div className="section-info">
                    <div className={`status-indicator ${isSectionFound('Содержание') ? 'found' : 'missing'}`}>
                      {isSectionFound('Содержание') ? '✓' : '✗'}
                    </div>
                    <div className="section-card">
                      <span className="section-name">Содержание</span>
                    </div>
                  </div>
                </div>
                <div className="structure-item">
                  <div className="section-info">
                    <div className={`status-indicator ${isSectionFound('Введение') ? 'found' : 'missing'}`}>
                      {isSectionFound('Введение') ? '✓' : '✗'}
                    </div>
                    <div className="section-card">
                      <span className="section-name">Введение</span>
                    </div>
                  </div>
                </div>
                <div className="structure-item">
                  <div className="section-info">
                    <div className={`status-indicator ${isSectionFound('Основная часть') ? 'found' : 'missing'}`}>
                      {isSectionFound('Основная часть') ? '✓' : '✗'}
                    </div>
                    <div className="section-card">
                      <span className="section-name">Основная часть</span>
                    </div>
                  </div>
                </div>
                <div className="structure-item">
                  <div className="section-info">
                    <div className={`status-indicator ${isSectionFound('Заключение') ? 'found' : 'missing'}`}>
                      {isSectionFound('Заключение') ? '✓' : '✗'}
                    </div>
                    <div className="section-card">
                      <span className="section-name">Заключение</span>
                    </div>
                  </div>
                </div>
                <div className="structure-item">
                  <div className="section-info">
                    <div className={`status-indicator ${isSectionFound('Библиография') ? 'found' : 'missing'}`}>
                      {isSectionFound('Библиография') ? '✓' : '✗'}
                    </div>
                    <div className="section-card">
                      <span className="section-name">Библиография</span>
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Компонент профиля
const Profile: React.FC = () => {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }
    fetchProfile();
    fetchReports();
  }, [navigate]);

  const fetchProfile = async () => {
    try {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('token', token!);

      const response = await fetch('/api/профиль', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setProfile(data);
      } else {
        navigate('/login');
      }
    } catch (error) {
      console.error('Ошибка загрузки профиля:', error);
    }
  };

  const fetchReports = async () => {
    try {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('token', token!);

      const response = await fetch('/api/мои-отчеты', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setReports(data.reports);
      }
    } catch (error) {
      console.error('Ошибка загрузки отчетов:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="container">Загрузка...</div>;
  }

  return (
    <div className="main-content">
      <h1>Профиль пользователя</h1>

      {profile && (
        <div className="profile-section">
          <h2>Информация о пользователе</h2>
          <p><strong>Имя пользователя:</strong> {profile.username}</p>
          <p><strong>Email:</strong> {profile.email || 'Не указан'}</p>
          <p><strong>Полное имя:</strong> {profile.full_name || 'Не указано'}</p>
        </div>
      )}

      <div className="profile-section">
        <h2>История проверок</h2>
        {reports.length === 0 ? (
          <p>Нет проверенных отчетов</p>
        ) : (
          <div>
            {reports.map(report => (
              <div key={report.id} className="report-item">
                <p><strong>Файл:</strong> {report.file}</p>
                <p><strong>Шаблон:</strong> {report.template}</p>
                <p><strong>Оценка:</strong> {report.score}%</p>
                <p><strong>Статус:</strong> {report.status}</p>
                <p><strong>Дата проверки:</strong> {new Date(report.upload_date).toLocaleString()}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// Главный компонент App
const App: React.FC = () => {
  return (
    <Router>
      <div>
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;