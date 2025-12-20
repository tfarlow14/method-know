<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import loader from '@monaco-editor/loader';
	import type { editor } from 'monaco-editor';

	interface Props {
		code?: string;
		readOnly?: boolean;
		language?: string;
		theme?: 'dark' | 'light';
		onCodeChange?: (code: string) => void;
	}

	let { 
		code = $bindable(''), 
		readOnly = false, 
		language = 'javascript',
		theme = 'dark',
		onCodeChange 
	}: Props = $props();

	let editorContainer: HTMLDivElement;
	let editorInstance: editor.IStandaloneCodeEditor | null = null;
	let isInternalUpdate = $state(false);

	// Auto-detect language from code content
	function detectLanguage(code: string): string {
		if (!code || code.trim().length === 0) {
			return 'javascript'; // Default
		}

		const trimmedCode = code.trim();

		// Check for shebangs
		if (trimmedCode.startsWith('#!/')) {
			if (trimmedCode.includes('python') || trimmedCode.includes('python3')) {
				return 'python';
			}
			if (trimmedCode.includes('node') || trimmedCode.includes('nodejs')) {
				return 'javascript';
			}
			if (trimmedCode.includes('bash') || trimmedCode.includes('sh')) {
				return 'javascript'; // Monaco doesn't have bash, use JS as fallback
			}
		}

		// Check for HTML patterns
		if (/<\s*html[\s>]|<\s*!DOCTYPE\s+html|<\s*div[\s>]|<\s*span[\s>]|<\s*body[\s>]|<\s*head[\s>]/i.test(trimmedCode)) {
			return 'html';
		}

		// Check for CSS patterns
		if (/^\s*[@#.][\w-]+\s*\{|^\s*[\w-]+\s*:\s*[^;]+;|@media|@import|@keyframes/i.test(trimmedCode)) {
			return 'css';
		}

		// Check for Python patterns
		if (
			/^\s*(def|class|import|from|if __name__|print\s*\(|lambda\s+\w+:)/m.test(trimmedCode) ||
			/:\s*$/.test(trimmedCode.split('\n')[0]) && !trimmedCode.includes('function') && !trimmedCode.includes('=>')
		) {
			return 'python';
		}

		// Check for TypeScript patterns (more specific than JS)
		if (
			/:\s*(string|number|boolean|any|void|object|Array<|Promise<|interface|type|enum|class\s+\w+)/.test(trimmedCode) ||
			/<\w+>/.test(trimmedCode) && /:\s*\w+/.test(trimmedCode) ||
			/export\s+(interface|type|enum|class)/.test(trimmedCode)
		) {
			return 'typescript';
		}

		// Check for JavaScript patterns
		if (
			/function\s+\w+|const\s+\w+\s*=\s*\(|let\s+\w+\s*=\s*\(|var\s+\w+|=>\s*\{|export\s+(default\s+)?function|module\.exports/.test(trimmedCode)
		) {
			return 'javascript';
		}

		// Default to JavaScript
		return 'javascript';
	}

	// Map language string to Monaco language ID
	function getMonacoLanguage(lang: string, code?: string): string {
		// If language is explicitly set and not 'auto', use it
		if (lang && lang.toLowerCase() !== 'auto' && lang.toLowerCase() !== '') {
			switch (lang.toLowerCase()) {
				case 'typescript':
				case 'ts':
					return 'typescript';
				case 'python':
				case 'py':
					return 'python';
				case 'html':
					return 'html';
				case 'css':
					return 'css';
				case 'javascript':
				case 'js':
					return 'javascript';
				default:
					// If unknown language, try auto-detection
					return code ? detectLanguage(code) : 'javascript';
			}
		}

		// Auto-detect if language is 'auto' or not provided
		return code ? detectLanguage(code) : 'javascript';
	}

	onMount(async () => {
		if (!editorContainer) return;

		try {
			// Load Monaco Editor
			const monaco = await loader.init();

			// Detect language from code if needed
			const detectedLanguage = getMonacoLanguage(language, code || '');

			// Create editor instance
			editorInstance = monaco.editor.create(editorContainer, {
				value: code || '',
				language: detectedLanguage,
				theme: theme === 'dark' ? 'vs-dark' : 'vs',
				readOnly: readOnly,
				automaticLayout: true,
				fontSize: 14,
				fontFamily: 'monospace',
				minimap: { enabled: false },
				scrollBeyondLastLine: false,
				wordWrap: 'on',
				formatOnPaste: true,
				formatOnType: false
			});

			// Listen for content changes
			if (!readOnly) {
				editorInstance.onDidChangeModelContent(() => {
					if (!isInternalUpdate && editorInstance) {
						const newCode = editorInstance.getValue();
						if (newCode !== code) {
							isInternalUpdate = true;
							code = newCode;
							onCodeChange?.(newCode);
							// Reset flag after a tick
							setTimeout(() => {
								isInternalUpdate = false;
							}, 0);
						}
					}
				});
			}

			// Update editor content when code prop changes externally
			$effect(() => {
				if (editorInstance && code !== undefined && !isInternalUpdate) {
					const currentContent = editorInstance.getValue();
					if (currentContent !== code) {
						isInternalUpdate = true;
						editorInstance.setValue(code);
						// Reset flag after a tick
						setTimeout(() => {
							isInternalUpdate = false;
						}, 0);
					}
				}
			});

			// Update language when it changes or code changes (for auto-detection)
			$effect(() => {
				if (editorInstance) {
					const monacoLang = getMonacoLanguage(language, code || '');
					monaco.editor.setModelLanguage(editorInstance.getModel()!, monacoLang);
				}
			});

			// Update theme when it changes
			$effect(() => {
				if (editorInstance) {
					monaco.editor.setTheme(theme === 'dark' ? 'vs-dark' : 'vs');
				}
			});

			// Update read-only state
			$effect(() => {
				if (editorInstance) {
					editorInstance.updateOptions({ readOnly: readOnly });
				}
			});

		} catch (error) {
			console.error('Failed to initialize Monaco Editor:', error);
		}
	});

	onDestroy(() => {
		if (editorInstance) {
			editorInstance.dispose();
			editorInstance = null;
		}
	});
</script>

<div bind:this={editorContainer} class="h-full w-full rounded-md overflow-hidden {readOnly ? '' : 'border border-slate-300'}"></div>

<style>
	:global(.monaco-editor) {
		border-radius: 0.375rem;
	}
</style>
