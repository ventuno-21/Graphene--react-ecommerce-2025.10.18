import { gql } from '@apollo/client';


export const GET_PRODUCTS = gql`
  query GetProducts {
    allProducts {
      id
      title
      price
      description
      image
      stock
      category {
        id
        name
      }
    }
  }
`;
export const GET_PRODUCT = gql`
  query GetProduct($id: ID!) {
    product(id: $id) {
      id
      title
      price
      description
      image
      stock
      category {
        id
        name
      }
    }
  }
`;
// Query to fetch the cart
export const GET_CART = gql`
  query Cart {
    cart {
      items {
        ... on CartItemType {
          product {
            id
            title
            price
            image 
            __typename
          }
          quantity
          totalPrice
          __typename
        }
        ... on GuestCartItemType {
          product {
            id
            title
            price
            image  
            __typename
          }
          quantity
          totalPrice
          __typename
        }
        __typename
      }
      totalItems
      totalPrice
    }
  }
`;