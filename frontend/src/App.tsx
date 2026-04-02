import { BrowserRouter, Route, Routes } from 'react-router-dom';
import Layout from './components/Layout';
import GenerationPage from './pages/GenerationPage';
import HistoryPage from './pages/HistoryPage';
import HomePage from './pages/HomePage';
import PreviewPage from './pages/PreviewPage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/generate/:jobId" element={<GenerationPage />} />
          <Route path="/preview/:podcastId" element={<PreviewPage />} />
          <Route path="/history" element={<HistoryPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
