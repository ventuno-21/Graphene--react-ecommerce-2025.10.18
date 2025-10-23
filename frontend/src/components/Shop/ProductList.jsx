import { useQuery, useMutation } from '@apollo/client';
import { Link } from 'react-router-dom';
import { GET_PRODUCTS, GET_CART } from '../../graphql/queries';
import { ADD_TO_CART } from '../../graphql/mutations';
import Swal from 'sweetalert2';

function ProductList() {
    const { loading, error, data } = useQuery(GET_PRODUCTS);
    const [addToCart] = useMutation(ADD_TO_CART, {
        refetchQueries: [{ query: GET_CART }],
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

    const truncateDescription = (text) => {
        const words = text.split(' ').slice(0, 8).join(' ');
        return words + (text.split(' ').length > 8 ? '...' : '');
    };

    if (loading) return <p className="text-center mt-20 text-gray-600 text-lg">Loading products...</p>;
    if (error) return <p className="text-center mt-20 text-red-600 text-lg">Error: {error.message}</p>;

    return (
        <div className="pt-20 max-w-7xl mx-auto p-6">
            <h2 className="text-3xl font-bold mb-8 text-center text-gray-900">Our Products</h2>
            {data.allProducts.length === 0 ? (
                <p className="text-center text-gray-600">No products available.</p>
            ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                    {data.allProducts.map((product) => (
                        <div
                            key={product.id}
                            className="bg-white rounded-lg shadow-inner shadow-md hover:shadow-inner hover:shadow-lg transition-all duration-300 overflow-hidden w-full flex flex-col"
                        >
                            <Link to={`/products/${product.id}`} className="w-full h-48">
                                <img
                                    src={product.image ? `http://localhost:5000/media/${product.image}` : 'https://placehold.co/400x300'}
                                    alt={product.title}
                                    className="w-full h-48 object-cover"
                                />
                            </Link>
                            <div className="p-6 flex flex-col flex-grow">
                                <div>
                                    <Link to={`/products/${product.id}`}>
                                        <h3 className="text-lg font-semibold mb-2 text-gray-900 hover:text-blue-600 transition-colors line-clamp-1">
                                            {product.title}
                                        </h3>
                                    </Link>
                                    <p className="text-gray-600 text-sm line-clamp-1">
                                        {truncateDescription(product.description || '')}
                                    </p>
                                </div>
                                <div className="mt-auto pt-3">
                                    <p className="text-blue-600 font-bold text-xl">${parseFloat(product.price).toFixed(2)}</p>
                                    <span className="text-sm text-green-600 mt-1 inline-block">In Stock: {product.stock}</span>
                                    <button
                                        onClick={() => addToCart({ variables: { productId: product.id, quantity: 1 } })}
                                        className="w-full mt-4 py-2 px-4 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
                                        disabled={product.stock === 0}
                                    >
                                        {product.stock === 0 ? 'Out of Stock' : 'Add to Cart'}
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

export default ProductList;
