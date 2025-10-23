import { Routes, Route } from 'react-router-dom';
import Login from './components/Auth/Login.jsx';
import Register from './components/Auth/Register.jsx';
import ActivateAccount from './components/Auth/ActivateAccount.jsx';
import ForgotPassword from './components/Auth/ForgotPassword.jsx';
import ResetPassword from './components/Auth/ResetPassword.jsx';
import ProductList from './components/Shop/ProductList.jsx';
import ProductDetail from './components/Shop/ProductDetail.jsx';
import Cart from './components/Shop/Cart.jsx';
import Navbar from './components/Navbar.jsx';

function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/activate/:token" element={<ActivateAccount />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password/:token" element={<ResetPassword />} />
        <Route path="/" element={<ProductList />} />
        <Route path="/products/:id" element={<ProductDetail />} />
        <Route path="/cart" element={<Cart />} />
      </Routes>
    </>
  );
}

export default App; // Ensure this line exists