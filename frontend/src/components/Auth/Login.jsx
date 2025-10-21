// src/components/Auth/Login.jsx
import { useState } from 'react'; // For state
import { useMutation } from '@apollo/client'; // For GraphQL
import { useNavigate } from 'react-router-dom'; // For redirect
import { LOGIN } from '../../graphql/mutations'; // Our mutation
import { useAuthStore } from '../../store/authStore'; // Global state
import Swal from 'sweetalert2'; // For alerts

function Login() {
    // State for form inputs
    const [email, setEmail] = useState(''); // email starts empty
    const [password, setPassword] = useState('');

    const navigate = useNavigate(); // To redirect
    const { login } = useAuthStore(); // From store

    // Mutation hook
    const [loginMutation] = useMutation(LOGIN, {
        onCompleted: (data) => { // When success
            login(data.login.accessToken); // Save token
            Swal.fire('Success', 'Logged in!', 'success');
            navigate('/'); // Go to home
        },
        onError: (error) => { // When error
            Swal.fire('Error', error.message, 'error');
        },
    });

    // Form submit handler
    const handleSubmit = (e) => {
        e.preventDefault(); // Stop page reload
        loginMutation({ variables: { email, password } }); // Call mutation
    };

    return (
        <div className="max-w-md mx-auto mt-8 p-6 bg-white rounded shadow"> {/* Tailwind styling */}
            <h2 className="text-2xl font-bold mb-4">Login</h2>
            <form onSubmit={handleSubmit}>
                <div className="mb-4">
                    <label className="block mb-1">Email</label>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)} // Update state
                        className="w-full p-2 border rounded"
                        required
                    />
                </div>
                <div className="mb-4">
                    <label className="block mb-1">Password</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full p-2 border rounded"
                        required
                    />
                </div>
                <button type="submit" className="w-full bg-blue-600 text-white p-2 rounded">
                    Login
                </button>
            </form>
            <p className="mt-4 text-center">
                <a href="/forgot-password" className="text-blue-600">Forgot Password?</a>
            </p>
        </div>
    );
}

export default Login;