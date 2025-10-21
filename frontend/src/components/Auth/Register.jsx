import { useState } from 'react';
import { useMutation } from '@apollo/client';
import { useNavigate } from 'react-router-dom';
import { REGISTER } from '../../graphql/mutations';
import Swal from 'sweetalert2';

function Register() {
    // State for form inputs
    const [email, setEmail] = useState('');
    const [password1, setPassword1] = useState('');
    const [password2, setPassword2] = useState('');

    const navigate = useNavigate();

    // Mutation to register user
    const [registerMutation] = useMutation(REGISTER, {
        onCompleted: (data) => {
            Swal.fire('Success', data.register.message, 'success');
            navigate('/login'); // Redirect to login after success
        },
        onError: (error) => {
            Swal.fire('Error', error.message, 'error');
        },
    });

    // Handle form submission
    const handleSubmit = (e) => {
        e.preventDefault();
        registerMutation({ variables: { email, password1, password2 } });
    };

    return (
        <div className="max-w-md mx-auto mt-8 p-6 bg-white rounded shadow">
            <h2 className="text-2xl font-bold mb-4">Register</h2>
            <form onSubmit={handleSubmit}>
                <div className="mb-4">
                    <label className="block mb-1">Email</label>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="w-full p-2 border rounded"
                        required
                    />
                </div>
                <div className="mb-4">
                    <label className="block mb-1">Password</label>
                    <input
                        type="password"
                        value={password1}
                        onChange={(e) => setPassword1(e.target.value)}
                        className="w-full p-2 border rounded"
                        required
                    />
                </div>
                <div className="mb-4">
                    <label className="block mb-1">Confirm Password</label>
                    <input
                        type="password"
                        value={password2}
                        onChange={(e) => setPassword2(e.target.value)}
                        className="w-full p-2 border rounded"
                        required
                    />
                </div>
                <button type="submit" className="w-full bg-blue-600 text-white p-2 rounded">
                    Register
                </button>
            </form>
            <p className="mt-4 text-center">
                <a href="/login" className="text-blue-600">Already have an account? Login</a>
            </p>
        </div>
    );
}

export default Register;