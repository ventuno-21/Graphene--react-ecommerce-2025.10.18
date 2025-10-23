import { useQuery, useMutation } from '@apollo/client';
import { useParams, Link } from 'react-router-dom';
import { useState } from 'react';
import { GET_PRODUCT, GET_CART } from '../../graphql/queries';
import { ADD_TO_CART } from '../../graphql/mutations';
import Swal from 'sweetalert2';

function ProductDetail() {
    const { id } = useParams();
    const { loading, error, data } = useQuery(GET_PRODUCT, {
        variables: { id },
    });

    const [quantity, setQuantity] = useState(1);

    const [addToCart] = useMutation(ADD_TO_CART, {
        refetchQueries: [{ query: GET_CART }], // ✅ This ensures navbar updates immediately
        onCompleted: () => {
            Swal.fire({
                title: 'Added to Cart!',
                icon: 'success',
                timer: 1500,
                showConfirmButton: false,
            });
        },
        onError: (err) => {
            Swal.fire('Error', err.message, 'error');
        },
    });

    if (loading) return <p className="text-center mt-20 text-gray-600 text-lg">Loading product...</p>;
    if (error) return <p className="text-center mt-20 text-red-600 text-lg">Error: {error.message}</p>;
    if (!data.product) return <p className="text-center mt-20 text-gray-600">Product not found.</p>;

    const { product } = data;

    const handleQuantityChange = (e) => {
        const value = parseInt(e.target.value);
        if (value >= 1 && value <= product.stock) {
            setQuantity(value);
        } else if (value > product.stock) {
            setQuantity(product.stock);
        } else {
            setQuantity(1);
        }
    };

    const handleAddToCart = () => {
        addToCart({ variables: { productId: product.id, quantity } });
    };

    return (
        <div className="pt-20 max-w-4xl mx-auto p-6">
            <Link to="/" className="text-blue-600 hover:text-blue-500 mb-6 inline-block">
                &larr; Back to Products
            </Link>
            <div className="bg-white rounded-lg shadow-inner shadow-md p-8 flex flex-col md:flex-row gap-8">
                <img
                    src={product.image ? `http://localhost:5000/media/${product.image}` : 'https://placehold.co/400x400'}
                    alt={product.title}
                    className="w-full md:w-1/2 h-96 object-cover rounded-lg"
                />
                <div className="flex-1">
                    <h1 className="text-3xl font-bold text-gray-900 mb-4">{product.title}</h1>
                    <p className="text-blue-600 font-bold text-2xl mb-4">${parseFloat(product.price).toFixed(2)}</p>
                    <p className="text-gray-600 mb-4">{product.description}</p>
                    <p className="text-green-600 mb-4">In Stock: {product.stock}</p>
                    <p className="text-gray-600 mb-6">Category: {product.category.name}</p>

                    <div className="mb-4">
                        <label htmlFor="quantity" className="block text-sm font-medium text-gray-700 mb-1">
                            Quantity
                        </label>
                        <input
                            type="number"
                            id="quantity"
                            min="1"
                            max={product.stock}
                            value={quantity}
                            onChange={handleQuantityChange}
                            className="w-24 p-2 border rounded-md text-center"
                        />
                    </div>

                    <button
                        onClick={handleAddToCart}
                        disabled={product.stock === 0}
                        className="w-full py-3 px-4 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
                    >
                        {product.stock === 0 ? 'Out of Stock' : `Add ${quantity} to Cart`}
                    </button>
                </div>
            </div>
        </div>
    );
}

export default ProductDetail;
