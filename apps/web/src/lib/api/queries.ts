import { queryOptions } from '@tanstack/svelte-query';
import { apiGet, apiPost } from './client';

// Example query keys - organize by resource type
export const queryKeys = {
	users: {
		all: ['users'] as const,
		lists: () => [...queryKeys.users.all, 'list'] as const,
		list: (filters: string) => [...queryKeys.users.lists(), { filters }] as const,
		details: () => [...queryKeys.users.all, 'detail'] as const,
		detail: (id: string) => [...queryKeys.users.details(), id] as const
	},
	resources: {
		all: ['resources'] as const,
		lists: () => [...queryKeys.resources.all, 'list'] as const,
		list: (filters: string) => [...queryKeys.resources.lists(), { filters }] as const,
		details: () => [...queryKeys.resources.all, 'detail'] as const,
		detail: (id: string) => [...queryKeys.resources.details(), id] as const
	},
	tags: {
		all: ['tags'] as const,
		lists: () => [...queryKeys.tags.all, 'list'] as const,
		list: (filters: string) => [...queryKeys.tags.lists(), { filters }] as const
	}
};

// Example: User queries
export const userQueries = {
	all: () =>
		queryOptions({
			queryKey: queryKeys.users.lists(),
			queryFn: () => apiGet('/users')
		}),
	detail: (id: string) =>
		queryOptions({
			queryKey: queryKeys.users.detail(id),
			queryFn: () => apiGet(`/users/${id}`)
		})
};

// Example: Resource queries
export const resourceQueries = {
	all: () =>
		queryOptions({
			queryKey: queryKeys.resources.lists(),
			queryFn: () => apiGet('/resources')
		}),
	detail: (id: string) =>
		queryOptions({
			queryKey: queryKeys.resources.detail(id),
			queryFn: () => apiGet(`/resources/${id}`)
		})
};

// Example: Tag queries
export const tagQueries = {
	all: () =>
		queryOptions({
			queryKey: queryKeys.tags.lists(),
			queryFn: () => apiGet('/tags')
		})
};

// User mutation types
export interface CreateUserData {
	first_name: string;
	last_name: string;
	email: string;
	password: string;
}

export interface UserResponse {
	id?: string;
	first_name: string;
	last_name: string;
	email: string;
}

export interface SignupResponse {
	user: UserResponse;
	token: string;
}

export interface LoginRequest {
	email: string;
	password: string;
}

export interface LoginResponse {
	user: UserResponse;
	token: string;
}

// Resource types
export interface ResourceBase {
	id?: string;
	title: string;
	description: string;
	user_id: string;
	tag_ids: string[];
}

export interface ArticleResource extends ResourceBase {
	type: 'article';
	url: string;
}

export interface CodeSnippetResource extends ResourceBase {
	type: 'code_snippet';
	code: string;
}

export interface LearningResource extends ResourceBase {
	type: 'learning_resource';
}

export type Resource = ArticleResource | CodeSnippetResource | LearningResource;

export interface ResourceCollection {
	resources: Resource[];
}

// Mutation functions
export const userMutations = {
	create: () => ({
		mutationFn: (data: CreateUserData): Promise<SignupResponse> =>
			apiPost<SignupResponse>('/users', data)
	}),
	login: () => ({
		mutationFn: (data: LoginRequest): Promise<LoginResponse> =>
			apiPost<LoginResponse>('/users/login', data)
	})
};

