import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ChatView from './pages/ChatView';
import HistoryPage from './pages/HistoryPage';

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<ChatView />} />
                <Route path="/history" element={<HistoryPage />} />
            </Routes>
        </BrowserRouter>
    )
}

export default App
