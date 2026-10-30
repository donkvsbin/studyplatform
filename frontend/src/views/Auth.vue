<script setup lang="ts">
import {computed,ref} from 'vue'
import {useRoute,useRouter} from 'vue-router'
import {useI18n} from 'vue-i18n'
import {ArrowRight,Check,Code2,Eye,EyeOff,Sparkles} from 'lucide-vue-next'
import {api,ApiError,json} from '../api'
import {useAuth} from '../stores/auth'
import {safeRedirect} from '../router'
import UiError from '../components/UiError.vue'
const {t,locale}=useI18n(),route=useRoute(),router=useRouter(),auth=useAuth()
const register=computed(()=>route.path==='/register')
const phone=ref(''),nickname=ref(''),password=ref(''),confirm=ref(''),show=ref(false),busy=ref(false),error=ref<unknown>(null)
async function submit(){
 error.value=null
 if(register.value&&password.value!==confirm.value){error.value=new ApiError('password_mismatch');return}
 busy.value=true
 try{
  if(register.value){await api('/auth/register',json('POST',{phone:phone.value,nickname:nickname.value,password:password.value,confirm_password:confirm.value,locale:locale.value}));password.value='';confirm.value='';await router.push({path:'/login',query:{...route.query,registered:'1'}})}
  else{await auth.login(phone.value,password.value);await router.push(safeRedirect(route.query.redirect))}
 }catch(e){error.value=e}finally{busy.value=false}
}
</script>
<template><div class="auth-page container"><aside class="auth-story"><span class="eyebrow light">{{t('auth.eyebrow')}}</span><h1>{{t('auth.quote')}}</h1><p>{{t('auth.quoteSub')}}</p><div class="auth-art"><div class="art-bracket">{</div><Code2 :size="72" :stroke-width="1"/><Sparkles class="art-spark" :size="30"/><div class="art-bracket">}</div></div><ul><li v-for="n in 3" :key="n"><Check :size="17"/>{{t(`auth.feature${n}`)}}</li></ul></aside>
 <section class="auth-form-wrap"><div class="auth-form"><span class="section-kicker">LEARN. BUILD. GROW.</span><h2>{{t(register?'auth.registerTitle':'auth.loginTitle')}}</h2><p class="muted">{{t(register?'auth.registerSubtitle':'auth.loginSubtitle')}}</p>
 <p v-if="route.query.registered&&!register" class="success-box" role="status">{{t('auth.registered')}}</p><p v-if="route.query.changed" class="success-box" role="status">{{t('auth.passwordChanged')}}</p><UiError :error="error"/>
 <form @submit.prevent="submit"><label v-if="register" for="nickname">{{t('auth.nickname')}}<input id="nickname" v-model="nickname" autocomplete="nickname" required maxlength="40"/></label>
 <label for="phone">{{t('auth.phone')}}<input id="phone" v-model="phone" type="tel" autocomplete="tel" required maxlength="20" placeholder="138 0000 0000" aria-describedby="phone-hint"/></label><small id="phone-hint" class="field-hint">{{t('auth.phoneHint')}}</small>
 <label for="password">{{t('auth.password')}}<span class="password-field"><input id="password" v-model="password" :type="show?'text':'password'" :autocomplete="register?'new-password':'current-password'" required minlength="8" maxlength="128" :placeholder="t('auth.passwordHint')"/><button type="button" class="icon-button" @click="show=!show" :aria-label="locale==='en'?(show?'Hide password':'Show password'):(show?'隐藏密码':'显示密码')"><EyeOff v-if="show" :size="18"/><Eye v-else :size="18"/></button></span></label>
 <label v-if="register" for="confirm">{{t('auth.confirm')}}<input id="confirm" v-model="confirm" :type="show?'text':'password'" autocomplete="new-password" required minlength="8" maxlength="128"/></label><button class="button wide" :disabled="busy">{{t(busy?'common.pending':register?'auth.submitRegister':'auth.submitLogin')}}<ArrowRight :size="18"/></button></form>
 <p class="auth-alternate">{{t(register?'auth.haveAccount':'auth.noAccount')}} <RouterLink :to="{path:register?'/login':'/register',query:{redirect:route.query.redirect}}">{{t(register?'auth.toLogin':'auth.toRegister')}}</RouterLink></p><p class="form-footnote">{{t(register?'auth.privacy':'auth.forgot')}}</p></div></section></div></template>
