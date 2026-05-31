<script lang="ts" setup>
import logoSvg from "@@/assets/images/layouts/logo.svg?url"
import logoText1Svg from "@@/assets/images/layouts/logo-text-1.svg?url"
import logoText2Svg from "@@/assets/images/layouts/logo-text-2.svg?url"
import { useLayoutMode } from "@@/composables/useLayoutMode"

interface Props {
  collapse?: boolean
}

const { collapse = true } = defineProps<Props>()

const { isLeft, isTop } = useLayoutMode()
</script>

<template>
  <div class="layout-logo-container" :class="{ 'collapse': collapse, 'layout-mode-top': isTop }">
    <transition name="layout-logo-fade">
      <router-link v-if="collapse" key="collapse" to="/">
        <img :src="logoSvg" class="layout-logo">
      </router-link>
      <router-link v-else key="expand" to="/">
        <img :src="!isLeft ? logoText2Svg : logoText1Svg" class="layout-logo-text">
      </router-link>
    </transition>
  </div>
</template>

<style lang="scss" scoped>
.layout-logo-container {
  position: relative;
  width: 100%;
  height: var(--v3-header-height);
  line-height: var(--v3-header-height);
  text-align: center;
  overflow: hidden;
  .layout-logo {
    display: none;
  }
  .layout-logo-text {
    height: 100%;
    vertical-align: middle;
  }
}

.layout-mode-top {
  height: var(--v3-navigationbar-height);
  line-height: var(--v3-navigationbar-height);
}

.collapse {
  .layout-logo {
    width: 32px;
    height: 32px;
    vertical-align: middle;
    display: inline-block;
  }
  .layout-logo-text {
    display: none;
  }
}
</style>
