import { createRoot } from 'react-dom/client'
import { Provider } from 'react-redux'
import { store } from './app/store'
import { fetchMe } from './features/auth/authSlice'
import { TOKEN_KEY } from './api/axiosClient'
import './index.css'
import App from './App.jsx'

// Có token thì lấy user trước khi người dùng thấy trang
if (localStorage.getItem(TOKEN_KEY)) store.dispatch(fetchMe())

createRoot(document.getElementById('root')).render(
  <Provider store={store}>
    <App />
  </Provider>
)