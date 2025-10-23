import React, { useEffect } from 'react';
import { useQuery, useMutation } from '@apollo/client';
import { Link } from 'react-router-dom';
import { GET_CART } from '../../graphql/queries';
import { UPDATE_CART_ITEM_QUANTITY, REMOVE_FROM_CART } from '../../graphql/mutations';
import Swal from 'sweetalert2';

// Extract base URL from VITE_API_URL (removes /graphql/)
const API_BASE_URL = import.meta.env.VITE_API_URL?.replace('/graphql/', '') || 'http://localhost:5000';

function Cart() {
    console.log("🔄 Cart component mounted");

    // Fetch cart data
    const { loading, error, data } = useQuery(GET_CART, {
        onCompleted: (fetchedData) => {
            console.log("✅ Cart query completed");
            console.log("📦 Raw cart data:", fetchedData);
        },
        onError: (queryError) => {
            console.error("❌ Error fetching cart:", queryError.message);
        }
    });

    // Mutation to update item quantity
    const [updateCartItemQuantity, { loading: updateLoading }] = useMutation(UPDATE_CART_ITEM_QUANTITY, {
        refetchQueries: [{ query: GET_CART }],
        awaitRefetchQueries: true, // Ensures cart is refreshed before UI updates
        onError: (err) => {
            console.error("❌ Error updating quantity:", err.message);
            Swal.fire('Error', err.message, 'error');
        },
    });

    // Mutation to remove item from cart
    const [removeFromCart, { loading: removeLoading }] = useMutation(REMOVE_FROM_CART, {
        refetchQueries: [{ query: GET_CART }],
        awaitRefetchQueries: true, // ✅ Fixes last-item-not-disappearing bug
        onCompleted: () => {
            console.log("🗑️ Item removed from cart");
            Swal.fire({
                title: 'Removed from Cart!',
                icon: 'success',
                timer: 1500,
                showConfirmButton: false,
            });
        },
        onError: (err) => {
            console.error("❌ Error removing item:", err.message);
            Swal.fire('Error', err.message, 'error');
        },
    });

    // Handle quantity change
    const handleUpdateQuantity = (cartItemId, quantity) => {
        console.log(`🔧 Updating quantity for item ${cartItemId} to ${quantity}`);
        if (quantity < 1) return;
        updateCartItemQuantity({
            variables: { cartItemId, quantity: parseInt(quantity) },
        });
    };

    // Handle item removal
    const handleRemoveFromCart = async (productId) => {
        console.log(`🗑️ Removing product ${productId} from cart`);
        await removeFromCart({ variables: { productId } });
    };

    // Log loading and error states
    useEffect(() => {
        if (loading) console.log("⏳ Cart query is loading...");
        if (error) console.log("⚠️ Cart query error:", error.message);
    }, [loading, error]);

    // Show loading or error messages
    if (loading) return <p className="text-center mt-20 text-gray-600 text-lg">Loading cart...</p>;
    if (error) return <p className="text-center mt-20 text-red-600 text-lg">Error: {error.message}</p>;

    const { cart } = data;
    console.log("📥 Final cart object:", cart);

    // Handle empty cart
    if (!cart || !cart.items || cart.items.length === 0) {
        console.log("🛒 Cart is empty or undefined");
        return (
            <div className="pt-20 max-w-7xl mx-auto p-6 text-center">
                <h2 className="text-3xl font-bold mb-8 text-gray-900">Your Cart</h2>
                <div className="text-center py-20">
                    <h3 className="text-2xl font-semibold text-gray-800 mb-4">Your cart is currently empty</h3>
                    <p className="text-gray-600 mb-6">
                        Looks like you haven’t added anything yet. Browse our products and fill it up!
                    </p>
                    <Link
                        to="/products"
                        className="inline-block px-6 py-3 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 transition-colors"
                    >
                        Shop Now
                    </Link>
                </div>
            </div>
        );
    }

    // Filter valid cart items (union types)
    const validItems = cart.items.filter(item =>
        item && (item.__typename === "CartItemType" || item.__typename === "GuestCartItemType")
    );
    console.log("🧮 Valid cart items:", validItems);

    return (
        <div className="pt-20 max-w-7xl mx-auto p-6">
            <h2 className="text-3xl font-bold mb-8 text-center text-gray-900">Your Cart</h2>
            <div className="bg-white rounded-lg shadow-md p-6">
                <ul className="divide-y divide-gray-200">
                    {validItems.map((item, index) => (
                        <li key={index} className="py-4 flex items-center justify-between">
                            <div className="flex items-center">
                                {/* Product image with fallback */}
                                {item.product.image ? (
                                    <img
                                        src={`${API_BASE_URL}/media/${item.product.image}`}
                                        alt={item.product.title}
                                        className="w-16 h-16 object-cover rounded mr-4"
                                    />
                                ) : (
                                    <img
                                        src="https://placehold.co/100x100"
                                        alt="Placeholder"
                                        className="w-16 h-16 object-cover rounded mr-4"
                                    />
                                )}
                                <div>
                                    <Link to={`/products/${item.product.id}`} className="text-lg font-semibold text-gray-900 hover:text-blue-600">
                                        {item.product.title}
                                    </Link>
                                    <p className="text-gray-600">Price: ${parseFloat(item.product.price).toFixed(2)}</p>
                                    <p className="text-gray-600">Total: ${parseFloat(item.totalPrice).toFixed(2)}</p>
                                </div>
                            </div>
                            <div className="flex items-center space-x-4">
                                {/* Quantity input */}
                                <input
                                    type="number"
                                    value={item.quantity}
                                    min="1"
                                    onChange={(e) => handleUpdateQuantity(item.id, e.target.value)}
                                    disabled={updateLoading}
                                    className="w-16 p-2 border rounded-md text-center"
                                />
                                {/* Remove button */}
                                <button
                                    onClick={() => handleRemoveFromCart(item.product.id)}
                                    disabled={removeLoading}
                                    className="py-2 px-4 bg-red-600 text-white font-medium rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors"
                                >
                                    {removeLoading ? 'Removing...' : 'Remove'}
                                </button>
                            </div>
                        </li>
                    ))}
                </ul>

                {/* Cart summary */}
                <div className="mt-6 text-right">
                    <p className="text-xl font-semibold text-gray-900">Total Items: {cart.totalItems}</p>
                    <p className="text-xl font-semibold text-gray-900">Total Price: ${parseFloat(cart.totalPrice).toFixed(2)}</p>
                </div>
            </div>
        </div>
    );
}

export default Cart;
