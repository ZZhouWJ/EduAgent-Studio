<script lang="ts" setup>
import { useTheme } from "@@/composables/useTheme"
import { useGreyAndColorWeakness } from "@@/composables/useGreyAndColorWeakness"
import zhCn from "element-plus/es/locale/lang/zh-cn"

const { initTheme } = useTheme()
const { initGreyAndColorWeakness } = useGreyAndColorWeakness()

initTheme()
initGreyAndColorWeakness()
</script>

<template>
  <el-config-provider :locale="zhCn">
    <router-view />
  </el-config-provider>
</template>
