import { useState } from 'react';
import { useMutation } from '@apollo/client';
import { REGISTER } from '../../graphql/mutations';
import Swal from 'sweetalert2';
import { Link, useNavigate } from 'react-router-dom';

function Register() {
    const [email, setEmail] = useState('');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const navigate = useNavigate();

    const [register] = useMutation(REGISTER, {
        onCompleted: (data) => {
            console.log('Mutation response:', data); // لاگ برای دیباگ
            Swal.fire({
                title: 'Success',
                text: 'Registration successful! Please check your email to activate your account.',
                icon: 'success',
                timer: 2000,
                showConfirmButton: false,
            });
            navigate('/login');
        },
        onError: (error) => {
            console.error('GraphQL Error:', error);
            Swal.fire('Error', error.message || 'Failed to register. Please try again.', 'error');
        },
    });

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!email || !username || !password || !confirmPassword) {
            Swal.fire('Error', 'All fields are required', 'error');
            return;
        }
        if (password !== confirmPassword) {
            Swal.fire('Error', 'Passwords do not match', 'error');
            return;
        }
        console.log('Sending variables:', { email, username, password1: password, password2: confirmPassword });
        register({ variables: { email, username, password1: password, password2: confirmPassword } });
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100 pt-20">
            <div className="max-w-md w-full bg-white rounded-xl shadow-lg p-8 space-y-6">
                <h2 className="text-3xl font-bold text-center text-gray-900">Register</h2>
                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                            Username
                        </label>
                        <input
                            id="username"
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            required
                        />
                    </div>
                    <div>
                        <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                            Email
                        </label>
                        <input
                            id="email"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            required
                        />
                    </div>
                    <div>
                        <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                            Password
                        </label>
                        <input
                            id="password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            required
                        />
                    </div>
                    <div>
                        <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">
                            Confirm Password
                        </label>
                        <input
                            id="confirmPassword"
                            type="password"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            required
                        />
                    </div>
                    <button
                        type="submit"
                        className="w-full py-2 px-4 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                        Register
                    </button>
                </form>
                <p className="text-center text-sm text-gray-600">
                    Already have an account?{' '}
                    <Link to="/login" className="text-blue-600 hover:text-blue-500">
                        Login
                    </Link>
                </p>
            </div>
        </div>
    );
}

export default Register;