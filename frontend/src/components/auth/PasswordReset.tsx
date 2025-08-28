import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Mail, ArrowLeft, Send, CheckCircle } from 'lucide-react';
import { Button } from '../common/Button';
import { Input } from '../common/Input';
import { toast } from 'react-hot-toast';

interface ResetFormData {
  email: string;
}

const PasswordReset: React.FC = () => {
  const [formData, setFormData] = useState<ResetFormData>({
    email: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [errors, setErrors] = useState<Partial<ResetFormData>>({});

  const validateForm = (): boolean => {
    const newErrors: Partial<ResetFormData> = {};

    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setIsSubmitted(true);
      toast.success('Password reset email sent! Check your inbox.');
    } catch {
      toast.error('Failed to send reset email. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
    
    // Clear error when user starts typing
    if (errors[name as keyof ResetFormData]) {
      setErrors(prev => ({
        ...prev,
        [name]: undefined,
      }));
    }
  };

  const handleResendEmail = async () => {
    setIsLoading(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      toast.success('Password reset email resent!');
    } catch {
      toast.error('Failed to resend email. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  if (isSubmitted) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <div className="mx-auto h-16 w-16 flex items-center justify-center bg-green-100 rounded-full">
              <CheckCircle className="h-10 w-10 text-green-600" />
            </div>
            <h2 className="mt-6 text-center text-3xl font-bold text-gray-900">
              Check your email
            </h2>
            <p className="mt-2 text-center text-sm text-gray-600">
              We've sent a password reset link to
            </p>
            <p className="text-center text-sm font-medium text-brand-600">
              {formData.email}
            </p>
          </div>

          <div className="bg-white shadow-soft rounded-lg p-6">
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                  <div className="h-6 w-6 bg-brand-100 rounded-full flex items-center justify-center">
                    <span className="text-brand-600 font-bold text-sm">1</span>
                  </div>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">Check your inbox</p>
                  <p className="text-sm text-gray-600">
                    Look for an email from Kanvert with the subject "Reset your password"
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                  <div className="h-6 w-6 bg-brand-100 rounded-full flex items-center justify-center">
                    <span className="text-brand-600 font-bold text-sm">2</span>
                  </div>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">Click the reset link</p>
                  <p className="text-sm text-gray-600">
                    The link will expire in 24 hours for security reasons
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                  <div className="h-6 w-6 bg-brand-100 rounded-full flex items-center justify-center">
                    <span className="text-brand-600 font-bold text-sm">3</span>
                  </div>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">Create a new password</p>
                  <p className="text-sm text-gray-600">
                    Choose a strong password that you haven't used before
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="text-center space-y-4">
            <p className="text-sm text-gray-600">
              Didn't receive the email? Check your spam folder or
            </p>
            <Button
              type="button"
              variant="outline"
              onClick={handleResendEmail}
              loading={isLoading}
              disabled={isLoading}
              className="w-full"
            >
              {isLoading ? 'Resending...' : 'Resend email'}
            </Button>
            
            <div className="pt-4">
              <Link
                to="/login"
                className="inline-flex items-center text-sm font-medium text-brand-600 hover:text-brand-500 transition-colors"
              >
                <ArrowLeft className="h-4 w-4 mr-1" />
                Back to sign in
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <div className="mx-auto h-12 w-12 flex items-center justify-center bg-brand-600 rounded-xl">
            <span className="text-white font-bold text-xl">K</span>
          </div>
          <h2 className="mt-6 text-center text-3xl font-bold text-gray-900">
            Reset your password
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Enter your email address and we'll send you a link to reset your password.
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700">
              Email address
            </label>
            <div className="mt-1">
              <Input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="Enter your email address"
                className={errors.email ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : ''}
                leftIcon={<Mail className="h-5 w-5 text-gray-400" />}
              />
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">{errors.email}</p>
              )}
            </div>
          </div>

          <div>
            <Button
              type="submit"
              variant="primary"
              size="lg"
              className="w-full"
              loading={isLoading}
              disabled={isLoading}
              rightIcon={<Send className="h-5 w-5" />}
            >
              {isLoading ? 'Sending reset link...' : 'Send reset link'}
            </Button>
          </div>

          <div className="text-center">
            <Link
              to="/login"
              className="inline-flex items-center text-sm font-medium text-brand-600 hover:text-brand-500 transition-colors"
            >
              <ArrowLeft className="h-4 w-4 mr-1" />
              Back to sign in
            </Link>
          </div>
        </form>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex">
            <div className="ml-3">
              <h3 className="text-sm font-medium text-blue-800">
                Security tip
              </h3>
              <div className="mt-2 text-sm text-blue-700">
                <p>
                  For your security, password reset links expire after 24 hours. 
                  If you don't receive an email within a few minutes, check your spam folder.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PasswordReset;