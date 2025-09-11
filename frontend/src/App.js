import Home from './pages/Home';
import Programming from './pages/Programming';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

function App() {
  return (

    <Router>
      <div className="App">
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/programacion" element={<Programming />} />
          </Routes>
        </main>
      </div>
    </Router>

  );
}

export default App;