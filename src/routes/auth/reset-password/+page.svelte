<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { onMount, getContext } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';

	import { resetPassword, verifyResetToken } from '$lib/apis/auths';
	import { WEBUI_BASE_URL } from '$lib/constants';
	import { WEBUI_NAME, config, user } from '$lib/stores';

	import Spinner from '$lib/components/common/Spinner.svelte';
	import SensitiveInput from '$lib/components/common/SensitiveInput.svelte';

	const i18n = getContext('i18n');

	let loaded = false;
	let token = '';
	let password = '';
	let confirmPassword = '';
	let isSubmitting = false;
	let isSuccess = false;
	let isValidToken = false;
	let isVerifying = true;

	const submitHandler = async () => {
		if (!password) {
			toast.error($i18n.t('Please enter a new password'));
			return;
		}

		if (password !== confirmPassword) {
			toast.error($i18n.t('Passwords do not match'));
			return;
		}

		isSubmitting = true;

		try {
			const res = await resetPassword(token, password);
			if (res) {
				isSuccess = true;
				toast.success($i18n.t('Your password has been reset successfully'));
			}
		} catch (error) {
			toast.error(`${error}`);
		} finally {
			isSubmitting = false;
		}
	};

	const verifyToken = async () => {
		try {
			const res = await verifyResetToken(token);
			if (res?.valid) {
				isValidToken = true;
			} else {
				toast.error($i18n.t('The password reset link is invalid or has expired'));
			}
		} catch (error) {
			toast.error($i18n.t('The password reset link is invalid or has expired'));
		} finally {
			isVerifying = false;
		}
	};

	onMount(async () => {
		if ($user !== undefined) {
			goto('/');
		}

		if (!$config?.features?.enable_password_reset) {
			toast.error($i18n.t('Password reset is not enabled'));
			goto('/auth');
			return;
		}

		token = $page.url.searchParams.get('token') || '';

		if (!token) {
			toast.error($i18n.t('Invalid password reset link'));
			goto('/auth');
			return;
		}

		await verifyToken();
		loaded = true;
	});
</script>

<svelte:head>
	<title>
		{$i18n.t('Reset Password')} | {`${$WEBUI_NAME}`}
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
						{#if isVerifying}
							<div class="flex flex-col items-center">
								<Spinner className="size-8" />
								<div class="mt-4 text-sm text-gray-600 dark:text-gray-400">
									{$i18n.t('Verifying reset link...')}
								</div>
							</div>
						{:else if !isValidToken}
							<div class="flex flex-col items-center">
								<div class="mb-4">
									<svg
										xmlns="http://www.w3.org/2000/svg"
										fill="none"
										viewBox="0 0 24 24"
										stroke-width="1.5"
										stroke="currentColor"
										class="size-16 text-red-500"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z"
										/>
									</svg>
								</div>
								<div class="text-2xl font-medium mb-2">
									{$i18n.t('Invalid or Expired Link')}
								</div>
								<div class="text-sm text-gray-600 dark:text-gray-400 mb-6">
									{$i18n.t('The password reset link is invalid or has expired. Please request a new one.')}
								</div>
								<a
									href="/auth/forgot-password"
									class="bg-gray-700/5 hover:bg-gray-700/10 dark:bg-gray-100/5 dark:hover:bg-gray-100/10 dark:text-gray-300 dark:hover:text-white transition rounded-full font-medium text-sm py-2.5 px-6"
								>
									{$i18n.t('Request New Link')}
								</a>
								<div class="mt-4">
									<a
										href="/auth"
										class="text-sm font-medium underline text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200"
									>
										{$i18n.t('Back to Sign In')}
									</a>
								</div>
							</div>
						{:else if isSuccess}
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
											d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"
										/>
									</svg>
								</div>
								<div class="text-2xl font-medium mb-2">
									{$i18n.t('Password Reset Successful')}
								</div>
								<div class="text-sm text-gray-600 dark:text-gray-400 mb-6">
									{$i18n.t('Your password has been reset successfully. You can now sign in with your new password.')}
								</div>
								<a
									href="/auth"
									class="bg-gray-700/5 hover:bg-gray-700/10 dark:bg-gray-100/5 dark:hover:bg-gray-100/10 dark:text-gray-300 dark:hover:text-white transition rounded-full font-medium text-sm py-2.5 px-6"
								>
									{$i18n.t('Sign In')}
								</a>
							</div>
						{:else}
							<form
								class="flex flex-col justify-center"
								on:submit={(e) => {
									e.preventDefault();
									submitHandler();
								}}
							>
								<div class="mb-1">
									<div class="text-2xl font-medium">
										{$i18n.t('Reset Password')}
									</div>
									<div class="mt-2 text-sm text-gray-600 dark:text-gray-400">
										{$i18n.t('Enter your new password below.')}
									</div>
								</div>

								<div class="flex flex-col mt-4">
									<div class="mb-2">
										<label for="password" class="text-sm font-medium text-left mb-1 block">
											{$i18n.t('New Password')}
										</label>
										<SensitiveInput
											bind:value={password}
											type="password"
											id="password"
											class="my-0.5 w-full text-sm outline-hidden bg-transparent placeholder:text-gray-300 dark:placeholder:text-gray-600"
											placeholder={$i18n.t('Enter New Password')}
											autocomplete="new-password"
											name="password"
											required
										/>
									</div>

									<div class="mb-2">
										<label for="confirm-password" class="text-sm font-medium text-left mb-1 block">
											{$i18n.t('Confirm New Password')}
										</label>
										<SensitiveInput
											bind:value={confirmPassword}
											type="password"
											id="confirm-password"
											class="my-0.5 w-full text-sm outline-hidden bg-transparent placeholder:text-gray-300 dark:placeholder:text-gray-600"
											placeholder={$i18n.t('Confirm New Password')}
											autocomplete="new-password"
											name="confirm-password"
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
										{$i18n.t('Reset Password')}
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
