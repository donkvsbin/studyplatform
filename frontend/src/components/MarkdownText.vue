<script setup lang="ts">
import { computed } from "vue";
import MarkdownIt from "markdown-it";
import DOMPurify from "dompurify";
const props = defineProps<{ text: string }>();
const markdown = new MarkdownIt({ html: false, linkify: false, breaks: true });
const html = computed(() =>
  DOMPurify.sanitize(markdown.render(props.text), {
    FORBID_TAGS: ["img", "iframe", "style", "form"],
    FORBID_ATTR: ["style"],
  }),
);
</script>
<template><div class="markdown-text" v-html="html"></div></template>
