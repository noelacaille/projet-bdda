<template>
	<div v-if="password" class="password-checker-box">
		<div class="password-strength">
			<div :class="passwordStrengthColor" class="strength-bar"></div>
		</div>
		<p :style="{ color: passwordStrengthTextColor }" class="strength-text">{{ passwordStrengthText }}</p>
		<ul class="password-conditions">
			<li :class="conditionClass(lengthCondition)">
				<svg v-if="lengthCondition" class="icon-check" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
					<path fill="green" d="M9 16.2l-4.2-4.2-1.4 1.4 5.6 5.6L20.3 8l-1.4-1.4z" />
				</svg>
				<svg v-else class="icon-cross" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
					<path fill="red"
						d="M18.3 5.7l-1.4-1.4L12 9.2 7.1 4.3 5.7 5.7l4.9 4.9-4.9 4.9 1.4 1.4 4.9-4.9 4.9 4.9 1.4-1.4-4.9-4.9z" />
				</svg>
				At least 8 characters
			</li>
			<li :class="conditionClass(uppercaseCondition)">
				<svg v-if="uppercaseCondition" class="icon-check" xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 24 24">
					<path fill="green" d="M9 16.2l-4.2-4.2-1.4 1.4 5.6 5.6L20.3 8l-1.4-1.4z" />
				</svg>
				<svg v-else class="icon-cross" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
					<path fill="red"
						d="M18.3 5.7l-1.4-1.4L12 9.2 7.1 4.3 5.7 5.7l4.9 4.9-4.9 4.9 1.4 1.4 4.9-4.9 4.9 4.9 1.4-1.4-4.9-4.9z" />
				</svg>
				One uppercase letter
			</li>
			<li :class="conditionClass(numberCondition)">
				<svg v-if="numberCondition" class="icon-check" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
					<path fill="green" d="M9 16.2l-4.2-4.2-1.4 1.4 5.6 5.6L20.3 8l-1.4-1.4z" />
				</svg>
				<svg v-else class="icon-cross" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
					<path fill="red"
						d="M18.3 5.7l-1.4-1.4L12 9.2 7.1 4.3 5.7 5.7l4.9 4.9-4.9 4.9 1.4 1.4 4.9-4.9 4.9 4.9 1.4-1.4-4.9-4.9z" />
				</svg>
				One number
			</li>
			<li :class="conditionClass(specialCharCondition)">
				<svg v-if="specialCharCondition" class="icon-check" xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 24 24">
					<path fill="green" d="M9 16.2l-4.2-4.2-1.4 1.4 5.6 5.6L20.3 8l-1.4-1.4z" />
				</svg>
				<svg v-else class="icon-cross" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
					<path fill="red"
						d="M18.3 5.7l-1.4-1.4L12 9.2 7.1 4.3 5.7 5.7l4.9 4.9-4.9 4.9 1.4 1.4 4.9-4.9 4.9 4.9 1.4-1.4-4.9-4.9z" />
				</svg>
				One special character
			</li>
		</ul>
	</div>
</template>

<script>
export default {
	props: ['password', 'confirmPassword'],
	data() {
		return {
			lengthCondition: false,
			uppercaseCondition: false,
			numberCondition: false,
			specialCharCondition: false,
		};
	},
	computed: {
		passwordStrengthColor() {
			if (this.passwordStrength === 1) return 'strength-too-weak';
			if (this.passwordStrength === 2) return 'strength-weak';
			if (this.passwordStrength === 3) return 'strength-medium';
			if (this.passwordStrength === 4) return 'strength-good';
			return 'strength-strong';
		},
		passwordStrengthText() {
			if (this.passwordStrength === 1) return 'Too weak';
			if (this.passwordStrength === 2) return 'Weak';
			if (this.passwordStrength === 3) return 'Medium';
			if (this.passwordStrength === 4) return 'Good';
			return 'Strong';
		},
		passwordStrengthTextColor() {
			if (this.passwordStrength === 1) return '#b90000';
			if (this.passwordStrength === 2) return '#c26100';
			if (this.passwordStrength === 3) return '#b3b301';
			if (this.passwordStrength === 4) return '#58af01';
			return '#006600';
		},
		passwordStrength() {
			return [
				this.lengthCondition,
				this.uppercaseCondition,
				this.numberCondition,
				this.specialCharCondition,
			].filter(Boolean).length + 1;
		},
	},
	watch: {
		password: 'checkPasswordStrength',
	},
	methods: {
		checkPasswordStrength() {
			this.lengthCondition = this.password.length >= 8;
			this.uppercaseCondition = /[A-Z]/.test(this.password);
			this.numberCondition = /\d/.test(this.password);
			this.specialCharCondition = /[!@#$%^&*(),.?":{}|<>+\-/]/.test(this.password);
		},
		conditionClass(conditionMet) {
			return conditionMet ? 'condition-met' : 'condition-unmet';
		},
	},
};
</script>

<style scoped>
.password-checker-box {
	margin-bottom: 30px;
}

.password-strength {
	width: 100%;
	height: 8px;
	background: #ccc;
	border-radius: 5px;
	overflow: hidden;
}

.strength-bar {
	height: 100%;
	transition: width 0.3s ease;
}

.strength-too-weak {
	width: 20%;
	background: #b90000;
}

.strength-weak {
	width: 40%;
	background: #c26100;
}

.strength-medium {
	width: 60%;
	background: #b3b301;
}

.strength-good {
	width: 80%;
	background: #58af01;
}

.strength-strong {
	width: 100%;
	background: #006600;
}

.strength-text {
	font-size: 12px;
	margin-top: 5px;
	color: #fff;
	text-align: center;
	font-weight: bold;
}

.password-conditions {
	display: grid;
	grid-template-columns: repeat(2, 1fr);
	list-style: none;
	padding: 0;
	margin: 10px 0;
	gap: 10px;
}

.password-conditions li {
	display: flex;
	align-items: center;
	font-size: 12px;
}

.condition-met {
	color: green;
}

.condition-unmet {
	color: red;
}

.icon-check,
.icon-cross {
	width: 15px;
	height: 15px;
	margin-right: 5px;
}
</style>
