import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import ArticlePage from './pages/ArticlePage';
import { HomeStateProvider } from './contexts/HomeStateContext';

function App() {
  return (
    <HomeStateProvider>
      <Router>
        <Routes>
          <Route path="/home" element={<HomePage />} />
          <Route path="/article" element={<ArticlePage />} />
          <Route path="*" element={<h1>404 - Not found</h1>} />
        </Routes>
      </Router>
    </HomeStateProvider>
  );
}

export default App;
