<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { onMount, getContext } from 'svelte';
	import { goto } from '$app/navigation';

	import { forgotPassword } from '$lib/apis/auths';
	import { WEBUI_BASE_URL } from '$lib/constants';
	import { WEBUI_NAME, config, user } from '$lib/stores';

	import Spinner from '$lib/components/common/Spinner.svelte';

	const i18n = getContext('i18n');

	let loaded = false;
	let email = '';
	let isSubmitting = false;
	let isSubmitted = false;

	const submitHandler = async () => {
		if (!email) {
			toast.error($i18n.t('Please enter your email address'));
			return;
		}

		isSubmitting = true;

		try {
			const res = await forgotPassword(email);
			if (res) {
				isSubmitted = true;
				toast.success($i18n.t('If an account exists with this email, you will receive a password reset link shortly.'));
			}
		} catch (error) {
			// Still show success message to prevent email enumeration
			isSubmitted = true;
			toast.success($i18n.t('If an account exists with this email, you will receive a password reset link shortly.'));
		} finally {
			isSubmitting = false;
		}
	};

	onMount(async () => {
		if ($user !== undefined) {
			goto('/');
		}

		if (!$config?.features?.enable_password_reset) {
			toast.error($i18n.t('Password reset is not enabled'));
			goto('/auth');
		}

		loaded = true;
	});
</script>

<svelte:head>
	<title>
		{$i18n.t('Forgot Password')} | {`${$WEBUI_NAME}`}
	</title>
</svelte:head>

<div class="w-full h-screen max-h-[100dvh] text-white relative">
	<div class="w-full h-full absolute top-0 left-0 bg-white dark:bg-black"></div>

	<div class="w-full absolute top-0 left-0 right-0 h-8 drag-region" />

	{#if loaded}
		<div
			class="fixed bg-transparent min-h-screen w-full flex justify-center font-primary z-50 text-black dark:text-white"
		>
			<div class="w-full px-10 min-h-screen flex flex-col text-center">
				<div class="my-auto flex flex-col justify-center items-center">
					<div class="sm:max-w-md my-auto pb-10 w-full dark:text-gray-100">
						{#if !isSubmitted}
							<form
								class="flex flex-col justify-center"
								on:submit={(e) => {
									e.preventDefault();
									submitHandler();
								}}
							>
								<div class="mb-1">
									<div class="text-2xl font-medium">
										{$i18n.t('Forgot Password')}
									</div>
									<div class="mt-2 text-sm text-gray-600 dark:text-gray-400">
										{$i18n.t('Enter your email address and we\'ll send you a link to reset your password.')}
									</div>
								</div>

								<div class="flex flex-col mt-4">
									<div class="mb-2">
										<label for="email" class="text-sm font-medium text-left mb-1 block">
											{$i18n.t('Email')}
										</label>
										<input
											bind:value={email}
											type="email"
											id="email"
											class="my-0.5 w-full text-sm outline-hidden bg-transparent placeholder:text-gray-300 dark:placeholder:text-gray-600"
											autocomplete="email"
											name="email"
											placeholder={$i18n.t('Enter Your Email')}
											required
										/>
									</div>
								</div>

								<div class="mt-5">
									<button
										class="bg-gray-700/5 hover:bg-gray-700/10 dark:bg-gray-100/5 dark:hover:bg-gray-100/10 dark:text-gray-300 dark:hover:text-white transition w-full rounded-full font-medium text-sm py-2.5 flex items-center justify-center"
										type="submit"
										disabled={isSubmitting}
									>
										{#if isSubmitting}
											<Spinner className="size-4 mr-2" />
										{/if}
										{$i18n.t('Send Reset Link')}
									</button>
								</div>

								<div class="mt-4 text-sm text-center">
									<a
										href="/auth"
										class="font-medium underline text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200"
									>
										{$i18n.t('Back to Sign In')}
									</a>
								</div>
							</form>
						{:else}
							<div class="flex flex-col items-center">
								<div class="mb-4">
									<svg
										xmlns="http://www.w3.org/2000/svg"
										fill="none"
										viewBox="0 0 24 24"
										stroke-width="1.5"
										stroke="currentColor"
										class="size-16 text-green-500"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											d="M21.75 6.75v10.5a2.25 2.25 0 0 1-2.25 2.25h-15a2.25 2.25 0 0 1-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25m19.5 0v.243a2.25 2.25 0 0 1-1.07 1.916l-7.5 4.615a2.25 2.25 0 0 1-2.36 0L3.32 8.91a2.25 2.25 0 0 1-1.07-1.916V6.75"
										/>
									</svg>
								</div>
								<div class="text-2xl font-medium mb-2">
									{$i18n.t('Check Your Email')}
								</div>
								<div class="text-sm text-gray-600 dark:text-gray-400 mb-6">
									{$i18n.t('If an account exists with this email, you will receive a password reset link shortly.')}
								</div>
								<div class="text-sm text-gray-500 dark:text-gray-500 mb-4">
									{$i18n.t("Didn't receive the email? Check your spam folder or")}
									<button
										type="button"
										class="underline hover:text-gray-700 dark:hover:text-gray-300"
										on:click={() => {
											isSubmitted = false;
											email = '';
										}}
									>
										{$i18n.t('try again')}
									</button>
								</div>
								<a
									href="/auth"
									class="font-medium underline text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200"
								>
									{$i18n.t('Back to Sign In')}
								</a>
							</div>
						{/if}
					</div>
				</div>
			</div>
		</div>

		<div class="fixed m-10 z-50">
			<div class="flex space-x-2">
				<div class="self-center">
					<img
						crossorigin="anonymous"
						src="{WEBUI_BASE_URL}/static/favicon.png"
						class="w-6 rounded-full"
						alt=""
					/>
				</div>
			</div>
		</div>
	{/if}
</div>
