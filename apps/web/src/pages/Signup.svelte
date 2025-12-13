<script lang="ts">
  import { goto } from "../lib/router"
  import { createMutation } from "@tanstack/svelte-query"
  import { setAuthToken } from "../lib/auth"
  import { currentUser } from "../lib/stores"
  import type { UserResponse } from "../lib/api/queries"
  import {
    userMutations,
    type CreateUserData,
    type SignupResponse,
  } from "../lib/api/queries"
  import { signupSchema, type SignupFormData } from "../lib/validations/signup"
  import type { ZodError } from "zod"
  import RegHeader from "../components/RegHeader.svelte"
  import { Card, CardContent, CardHeader, CardTitle } from "$lib/components/ui/card"
  import { Input } from "$lib/components/ui/input"
  import { Label } from "$lib/components/ui/label"
  import { Button } from "$lib/components/ui/button"
  import { Loader2 } from "@lucide/svelte"

  let email = $state("")
  let password = $state("")
  let firstName = $state("")
  let lastName = $state("")
  let fieldErrors = $state<Record<string, string>>({})

  function validateForm(): boolean {
    fieldErrors = {}

    try {
      const formData: SignupFormData = {
        first_name: firstName,
        last_name: lastName,
        email: email,
        password: password,
      }

      signupSchema.parse(formData)
      return true
    } catch (err) {
      if (err instanceof Error && err.name === "ZodError") {
        const zodError = err as unknown as ZodError<SignupFormData>
        const errors: Record<string, string> = {}

        zodError.issues.forEach((issue) => {
          const path = issue.path[0] as string
          if (path) {
            errors[path] = issue.message
          }
        })

        fieldErrors = errors
      }
      return false
    }
  }

  const signupMutation = createMutation(() => ({
    ...userMutations.create(),
    onSuccess: (data: SignupResponse) => {
      // Store auth token in localStorage
      setAuthToken(data.token)
      
      // Store user info in Svelte store
      currentUser.set(data.user)

      // Redirect to root (dashboard) on success
      goto("/")
    },
}))

  function handleSubmit() {
    if (!validateForm()) {
      return
    }

    const userData: CreateUserData = {
      first_name: firstName.trim(),
      last_name: lastName.trim(),
      email: email.trim(),
      password: password,
    }

    signupMutation.mutate(userData)
  }
</script>

<div class="min-h-screen flex items-center justify-center bg-background px-4 py-8">
  <div class="w-full max-w-[480px] space-y-6">
    <RegHeader title="Join Method Know" />
    
    <Card class="gap-2 py-0 rounded-2xl p-4 bg-white shadow-none border border-slate-900/12 flex flex-col overflow-hidden box-border">
      <CardHeader class="pb-0 px-0">
        <CardTitle class="text-lg font-normal text-left py-2.5 leading-7 text-slate-900">Sign up</CardTitle>
      </CardHeader>
      <CardContent class="pt-0 px-0 w-full box-border">
        <form
          class="flex flex-col gap-4 w-full box-border"
          onsubmit={(e) => {
            e.preventDefault()
            handleSubmit()
          }}
        >
          <div class="grid grid-cols-2 gap-4 w-full min-w-0">
            <div class="flex flex-col gap-1.5 w-full min-w-0">
              <Label for="first-name" class="text-sm font-medium leading-5 text-slate-900">
                First Name
              </Label>
              <Input
                id="first-name"
                name="first-name"
                type="text"
                autocomplete="given-name"
                required
                bind:value={firstName}
                placeholder="John"
                class="h-auto w-full max-w-full rounded-md border-slate-300 placeholder:text-slate-400 text-base leading-6 pl-3 pr-3 py-2 bg-white box-border"
                aria-invalid={fieldErrors.first_name ? "true" : undefined}
              />
              {#if fieldErrors.first_name}
                <p class="text-sm text-destructive mt-1">{fieldErrors.first_name}</p>
              {/if}
            </div>
            <div class="flex flex-col gap-1.5 w-full min-w-0">
              <Label for="last-name" class="text-sm font-medium leading-5 text-slate-900">
                Last Name
              </Label>
              <Input
                id="last-name"
                name="last-name"
                type="text"
                autocomplete="family-name"
                required
                bind:value={lastName}
                placeholder="Doe"
                class="h-auto w-full max-w-full rounded-md border-slate-300 placeholder:text-slate-400 text-base leading-6 pl-3 pr-3 py-2 bg-white box-border"
                aria-invalid={fieldErrors.last_name ? "true" : undefined}
              />
              {#if fieldErrors.last_name}
                <p class="text-sm text-destructive mt-1">{fieldErrors.last_name}</p>
              {/if}
            </div>
          </div>
          
          {#if signupMutation.isError && signupMutation.error}
            <div class="rounded-md bg-red-50 p-4">
              <div class="flex">
                <div class="shrink-0">
                  <svg
                    class="h-5 w-5 text-red-400"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fill-rule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                      clip-rule="evenodd"
                    />
                  </svg>
                </div>
                <div class="ml-3">
                  <p class="text-sm font-medium text-red-800">
                    {signupMutation.error.message || "An error occurred during signup"}
                  </p>
                </div>
              </div>
            </div>
          {/if}
          
          <div class="flex flex-col gap-1.5 w-full min-w-0">
            <Label for="email" class="text-sm font-medium leading-5 text-slate-900">
              Email
            </Label>
            <Input
              id="email"
              name="email"
              type="email"
              autocomplete="email"
              required
              bind:value={email}
              placeholder="Enter your email"
              class="h-auto w-full max-w-full rounded-md border-slate-300 placeholder:text-slate-400 text-base leading-6 pl-3 pr-3 py-2 bg-white box-border"
              aria-invalid={fieldErrors.email ? "true" : undefined}
            />
            {#if fieldErrors.email}
              <p class="text-sm text-destructive mt-1">{fieldErrors.email}</p>
            {/if}
          </div>
          
          <div class="flex flex-col gap-1.5 w-full min-w-0">
            <Label for="password" class="text-sm font-medium leading-5 text-slate-900">
              Password
            </Label>
            <Input
              id="password"
              name="password"
              type="password"
              autocomplete="new-password"
              required
              bind:value={password}
              placeholder="Enter your password"
              class="h-auto w-full max-w-full rounded-md border-slate-300 placeholder:text-slate-400 text-base leading-6 pl-3 pr-3 py-2 bg-white box-border"
              aria-invalid={fieldErrors.password ? "true" : undefined}
            />
            {#if fieldErrors.password}
              <p class="text-sm text-destructive mt-1">{fieldErrors.password}</p>
            {/if}
          </div>
          
          <Button
            type="submit"
            disabled={signupMutation.isPending}
            variant="default"
            class="w-full h-auto rounded-md bg-slate-900 hover:bg-slate-900/90 font-medium text-sm leading-6 px-4 py-2"
            style="color: white !important;"
          >
            {#if signupMutation.isPending}
              <Loader2 class="mr-2 h-4 w-4 animate-spin" style="color: white;" />
              <span style="color: white;">Creating account...</span>
            {:else}
              <span style="color: white;">Sign up</span>
            {/if}
          </Button>
          
          <div class="flex items-center justify-center gap-2 text-base leading-7 text-slate-900 font-normal">
            <p>Already have an account?</p>
            <button
              type="button"
              onclick={() => goto("/login")}
              class="underline text-slate-900 leading-7 bg-transparent border-none p-0 cursor-pointer hover:text-slate-900/80 transition-colors"
            >
              Sign in
            </button>
          </div>
        </form>
      </CardContent>
    </Card>
  </div>
</div>
