import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { useQuery } from '@apollo/client';
import { GET_CART } from '../graphql/queries';
import { useState } from 'react';

function Navbar() {
    const { user, logout } = useAuthStore();
    const navigate = useNavigate();
    const [showCartDropdown, setShowCartDropdown] = useState(false);

    const { data } = useQuery(GET_CART);
    const cartItems = data?.cart?.items || [];
    const totalItems = data?.cart?.totalItems || 0;

    const handleLogout = async () => {
        await logout();
        navigate('/login');
    };

    return (
        <nav className="bg-blue-600 text-white p-4 shadow-md fixed w-full z-10">
            <div className="max-w-7xl mx-auto flex justify-between items-center relative">
                <Link to="/" className="text-2xl font-bold hover:text-blue-300">My Shop</Link>
                <div className="flex items-center space-x-6">
                    {/* <Link to="/" className="hover:text-blue-300 transition-colors">Products</Link> */}

                    {/* Cart Icon */}
                    <div className="relative">
                        <button
                            onClick={() => setShowCartDropdown(!showCartDropdown)}
                            className="relative hover:text-blue-300 transition-colors"
                        >
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                fill="none"
                                viewBox="0 0 24 24"
                                strokeWidth={1.5}
                                stroke="currentColor"
                                className="w-6 h-6"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    d="M2.25 3h1.386c.51 0 .955.343 1.09.835l.383 1.437m0 0l1.35 5.063m-.75-5.063h12.008c.708 0 1.22.66 1.056 1.35l-1.386 6.05a1.125 1.125 0 01-1.096.85H8.25m-2.25 0h-.75m0 0L4.5 18.75m0 0h13.5m-13.5 0a1.5 1.5 0 003 0m10.5 0a1.5 1.5 0 003 0"
                                />
                            </svg>
                            {totalItems > 0 && (
                                <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full px-1.5 py-0.5">
                                    {totalItems}
                                </span>
                            )}
                        </button>

                        {/* Cart Dropdown */}
                        {showCartDropdown && (
                            <div className="absolute right-0 mt-2 w-64 bg-white text-black rounded-md shadow-lg z-20">
                                <div className="p-4 border-b font-semibold">Cart Preview</div>
                                <ul className="max-h-64 overflow-y-auto">
                                    {cartItems.slice(0, 4).map((item, index) => (
                                        <li key={index} className="px-4 py-2 border-b text-sm">
                                            {item.product.title} × {item.quantity}
                                        </li>
                                    ))}
                                    {cartItems.length === 0 && (
                                        <li className="px-4 py-2 text-sm text-gray-500">Cart is empty</li>
                                    )}
                                </ul>
                                <div className="p-4">
                                    <Link
                                        to="/cart"
                                        className="block w-full text-center bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition-colors"
                                    >
                                        Go to Cart
                                    </Link>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Auth Links */}
                    {user ? (
                        <>
                            <span className="text-sm">Welcome, {user.email}</span>
                            <button onClick={handleLogout} className="hover:text-blue-300 transition-colors">Logout</button>
                        </>
                    ) : (
                        <>
                            <Link to="/login" className="hover:text-blue-300 transition-colors">Login</Link>
                            <Link to="/register" className="hover:text-blue-300 transition-colors">Register</Link>
                        </>
                    )}
                </div>
            </div>
        </nav>
    );
}

export default Navbar;
