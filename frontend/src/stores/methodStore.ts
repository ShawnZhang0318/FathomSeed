import { reactive } from 'vue'
import type { MethodOption } from '../types'

export const methodStore = reactive({
  methods: [] as MethodOption[],
  selected: ['mixed'] as string[],
  setMethods(methods: MethodOption[]) {
    this.methods = methods
  },
  toggle(code: string) {
    if (code === 'mixed') {
      this.selected = ['mixed']
      return
    }
    const withoutMixed = this.selected.filter((item) => item !== 'mixed')
    this.selected = withoutMixed.includes(code)
      ? withoutMixed.filter((item) => item !== code)
      : [...withoutMixed, code]
    if (this.selected.length === 0) {
      this.selected = ['mixed']
    }
  }
})

