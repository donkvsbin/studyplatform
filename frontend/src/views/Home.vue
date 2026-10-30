<script setup lang="ts">import {useI18n} from 'vue-i18n';const {t}=useI18n()</script>
<template><div class="container page"><h1>LearnHub · {{t('common.brand')}}</h1><RouterLink class="button" to="/register">{{t('nav.register')}}</RouterLink></div></template>
