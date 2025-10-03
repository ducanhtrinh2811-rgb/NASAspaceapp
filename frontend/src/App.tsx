import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import TopicPage from "./pages/TopicPage";
import Page4 from "./pages/Page4";
import { HomeStateProvider } from "./contexts/HomeStateContext";

function App() {
    return (
        <HomeStateProvider>
            <Router>
                <Routes>
                    <Route path="/" element={<HomePage />} />
                    <Route path="/topic/:id" element={<TopicPage />} />
                    <Route path="/article" element={<Page4 />} />
                    <Route
                        path="*"
                        element={
                            <h1 className="text-center mt-20 text-2xl">
                                404 - Not found
                            </h1>
                        }
                    />
                </Routes>
            </Router>
        </HomeStateProvider>
    );
}

export default App;