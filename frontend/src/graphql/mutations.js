import { gql } from '@apollo/client';

export const LOGIN = gql`
  mutation Login($email: String!, $password: String!) {
    login(email: $email, password: $password) {
      accessToken
      success
    }
  }
`;

export const REGISTER = gql`
  mutation Register($email: String!, $password1: String!, $password2: String!) {
    register(email: $email, password1: $password1, password2: $password2) {
      userId
      email
      message
      success
    }
  }
`;

export const LOGOUT = gql`
  mutation Logout {
    logout {
      success
    }
  }
`;

export const REFRESH_TOKEN = gql`
  mutation RefreshToken {
    refreshToken {
      accessToken
    }
  }
`;

export const ACTIVATE_ACCOUNT = gql`
  mutation ActivateAccount($token: String!) {
    activateAccount(token: $token) {
      success
    }
  }
`;

export const FORGOT_PASSWORD = gql`
  mutation ForgotPassword($email: String!) {
    forgotPassword(email: $email) {
      success
    }
  }
`;

export const RESET_PASSWORD = gql`
  mutation ResetPassword($token: String!, $password1: String!, $password2: String!) {
    resetPassword(token: $token, password1: $password1, password2: $password2) {
      success
    }
  }
`;