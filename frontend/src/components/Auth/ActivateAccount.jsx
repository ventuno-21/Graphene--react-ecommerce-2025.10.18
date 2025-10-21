// src/components/Auth/ActivateAccount.jsx
import { useEffect, useState } from 'react';
import { useMutation } from '@apollo/client';
import { useParams, useNavigate } from 'react-router-dom';
import { ACTIVATE_ACCOUNT } from '../../graphql/mutations';
import Swal from 'sweetalert2';

function ActivateAccount() {
    const { token } = useParams(); // Get token from URL like /activate/abc123
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const [activateAccount] = useMutation(ACTIVATE_ACCOUNT, {
        onCompleted: (data) => {
            setLoading(false);
            Swal.fire('Success', 'Account activated successfully! You can now log in.', 'success');
            navigate('/login');
        },
        onError: (err) => {
            setLoading(false);
            setError(err.message);
            Swal.fire('Error', err.message, 'error');
        },
    });

    useEffect(() => {
        if (token) {
            activateAccount({ variables: { token } });
        } else {
            setLoading(false);
            setError('No activation token provided');
            Swal.fire('Error', 'Invalid activation link', 'error');
        }
    }, [token, activateAccount]);

    if (loading) {
        return (
            <div className="max-w-md mx-auto mt-8 p-6 bg-white rounded shadow">
                <h2 className="text-2xl font-bold mb-4">Activating Account</h2>
                <p>Processing your activation...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="max-w-md mx-auto mt-8 p-6 bg-white rounded shadow">
                <h2 className="text-2xl font-bold mb-4">Activation Failed</h2>
                <p className="text-red-600">{error}</p>
                <a href="/register" className="text-blue-600 mt-4 inline-block">Try registering again</a>
            </div>
        );
    }

    return (
        <div className="max-w-md mx-auto mt-8 p-6 bg-white rounded shadow">
            <h2 className="text-2xl font-bold mb-4">Account Activated</h2>
            <p>Your account has been activated successfully!</p>
            <a href="/login" className="text-blue-600 mt-4 inline-block">Go to Login</a>
        </div>
    );
}

export default ActivateAccount;