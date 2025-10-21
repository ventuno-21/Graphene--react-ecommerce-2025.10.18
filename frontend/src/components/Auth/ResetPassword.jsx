// src/components/Auth/ResetPassword.jsx
import { useState } from 'react';
import { useMutation } from '@apollo/client';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { RESET_PASSWORD } from '../../graphql/mutations';
import Swal from 'sweetalert2';

function ResetPassword() {
    const [password1, setPassword1] = useState('');
    const [password2, setPassword2] = useState('');
    const [loading, setLoading] = useState(false);
    const { token } = useParams();
    const navigate = useNavigate();

    const [resetPassword] = useMutation(RESET_PASSWORD, {
        onCompleted: (data) => {
            setLoading(false);
            Swal.fire({
                title: 'Password Reset Successful!',
                text: 'Your password has been updated. You can now log in with your new password.',
                icon: 'success',
                confirmButtonText: 'Go to Login'
            }).then(() => {
                navigate('/login');
            });
        },
        onError: (error) => {
            setLoading(false);
            Swal.fire('Error', error.message, 'error');
        },
    });

    const handleSubmit = (e) => {
        e.preventDefault();
        if (password1 !== password2) {
            Swal.fire('Error', 'Passwords do not match', 'error');
            return;
        }
        if (password1.length < 6) {
            Swal.fire('Error', 'Password must be at least 6 characters', 'error');
            return;
        }
        setLoading(true);
        resetPassword({ variables: { token, password1, password2 } });
    };

    if (!token) {
        return (
            <div className="max-w-md mx-auto mt-8 p-6 bg-white rounded shadow">
                <h2 className="text-2xl font-bold mb-4 text-red-600">Invalid Reset Link</h2>
                <p>The password reset link is invalid or has expired.</p>
                <Link to="/forgot-password" className="text-blue-600 mt-4 inline-block">
                    Request a new reset link
                </Link>
            </div>
        );
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full space-y-8">
                <div>
                    <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
                        Reset Password
                    </h2>
                    <p className="mt-2 text-center text-sm text-gray-600">
                        Enter your new password twice to reset your account.
                    </p>
                </div>
                <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                    <div className="space-y-1">
                        <label htmlFor="password1" className="block text-sm font-medium text-gray-700">
                            New Password
                        </label>
                        <input
                            id="password1"
                            name="password1"
                            type="password"
                            required
                            value={password1}
                            onChange={(e) => setPassword1(e.target.value)}
                            className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                            placeholder="Enter new password"
                            autoComplete="new-password"
                            minLength="6"
                        />
                    </div>

                    <div className="space-y-1">
                        <label htmlFor="password2" className="block text-sm font-medium text-gray-700">
                            Confirm New Password
                        </label>
                        <input
                            id="password2"
                            name="password2"
                            type="password"
                            required
                            value={password2}
                            onChange={(e) => setPassword2(e.target.value)}
                            className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                            placeholder="Confirm new password"
                            autoComplete="new-password"
                        />
                    </div>

                    <div>
                        <button
                            type="submit"
                            disabled={loading || password1 !== password2}
                            className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {loading ? 'Resetting...' : 'Reset Password'}
                        </button>
                    </div>

                    <div className="text-center">
                        <Link to="/login" className="text-blue-600 hover:text-blue-500">
                            Back to Login
                        </Link>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default ResetPassword;