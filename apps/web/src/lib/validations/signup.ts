import { z } from 'zod';

export const signupSchema = z.object({
	first_name: z
		.string()
		.min(1, 'First name is required')
		.min(2, 'First name must be at least 2 characters')
		.max(50, 'First name must be less than 50 characters')
		.trim(),
	last_name: z
		.string()
		.min(1, 'Last name is required')
		.min(2, 'Last name must be at least 2 characters')
		.max(50, 'Last name must be less than 50 characters')
		.trim(),
	email: z.string().min(1, 'Email is required').email('Please enter a valid email address'),
	password: z
		.string()
		.min(1, 'Password is required')
		.min(8, 'Password must be at least 8 characters')
		.max(100, 'Password must be less than 100 characters')
});

export type SignupFormData = z.infer<typeof signupSchema>;

