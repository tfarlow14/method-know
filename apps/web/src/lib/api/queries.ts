import { queryOptions } from '@tanstack/svelte-query';
import { apiGet, apiPost, apiPut, apiDelete } from './client';

// Example query keys - organize by resource type
export const queryKeys = {
	users: {
		all: ['users'] as const,
		lists: () => [...queryKeys.users.all, 'list'] as const,
		list: (filters: string) => [...queryKeys.users.lists(), { filters }] as const,
		details: () => [...queryKeys.users.all, 'detail'] as const,
		detail: (id: string) => [...queryKeys.users.details(), id] as const,
		me: () => [...queryKeys.users.all, 'me'] as const
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
		}),
	me: () =>
		queryOptions({
			queryKey: queryKeys.users.me(),
			queryFn: () => apiGet<UserResponse>('/users/me')
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

// Tag types
export interface TagResponse {
	id?: string;
	name: string;
}

export interface TagCollection {
	tags: TagResponse[];
}

// Example: Tag queries
export const tagQueries = {
	all: () =>
		queryOptions({
			queryKey: queryKeys.tags.lists(),
			queryFn: () => apiGet<TagCollection>('/tags')
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
export const RESOURCE_TYPES = {
	ARTICLE: 'article',
	CODE_SNIPPET: 'code_snippet',
	BOOK: 'book',
	COURSE: 'course'
} as const;

export type ResourceType = (typeof RESOURCE_TYPES)[keyof typeof RESOURCE_TYPES];

export interface ResourceBase {
	id?: string;
	title: string;
	description: string;
	user: UserResponse; // Required: populated user information from backend
	tags: TagResponse[]; // Optional: 0 to many tags (empty array if none)
	created_at?: string; // ISO 8601 datetime string (optional for backward compatibility)
}

export interface ArticleResource extends ResourceBase {
	type: typeof RESOURCE_TYPES.ARTICLE;
	url: string;
}

export interface CodeSnippetResource extends ResourceBase {
	type: typeof RESOURCE_TYPES.CODE_SNIPPET;
	code: string;
}

export interface BookResource extends ResourceBase {
	type: typeof RESOURCE_TYPES.BOOK;
}

export interface CourseResource extends ResourceBase {
	type: typeof RESOURCE_TYPES.COURSE;
}

export type Resource = ArticleResource | CodeSnippetResource | BookResource | CourseResource;

export interface ResourceCollection {
	resources: Resource[];
}

// Resource input types
export interface ArticleResourceInput {
	type: typeof RESOURCE_TYPES.ARTICLE;
	title: string;
	description: string;
	url: string;
	tag_ids: string[];
}

export interface CodeSnippetResourceInput {
	type: typeof RESOURCE_TYPES.CODE_SNIPPET;
	title: string;
	description: string;
	code: string;
	tag_ids: string[];
}

export interface BookResourceInput {
	type: typeof RESOURCE_TYPES.BOOK;
	title: string;
	description: string;
	tag_ids: string[];
}

export interface CourseResourceInput {
	type: typeof RESOURCE_TYPES.COURSE;
	title: string;
	description: string;
	url?: string;
	tag_ids: string[];
}

export type ResourceInput = ArticleResourceInput | CodeSnippetResourceInput | BookResourceInput | CourseResourceInput;

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

export const resourceMutations = {
	create: () => ({
		mutationFn: (data: ResourceInput): Promise<Resource> =>
			apiPost<Resource>('/resources', data)
	}),
	update: () => ({
		mutationFn: ({ id, data }: { id: string; data: ResourceInput }): Promise<Resource> =>
			apiPut<Resource>(`/resources/${id}`, data)
	}),
	delete: () => ({
		mutationFn: (id: string): Promise<void> =>
			apiDelete<void>(`/resources/${id}`)
	})
};

export const tagMutations = {
	create: () => ({
		mutationFn: (data: { name: string }): Promise<TagResponse> =>
			apiPost<TagResponse>('/tags', data)
	})
};

