<template>
    <div
        class="shadow-xl bg-white rounded-lg flex flex-col justify-between items-start dark:bg-slate-600 dark:text-white py-4 px-8 w-10/12 sm:w-8/12 md:6/12 lg:w-6/12 xl:w-96">

        <div class="w-full text-gradient-blue-red font-semibold text-3xl my-2">日历订阅链接</div>
        <span class="my-1 border border-slate-200 rounded-md p-2 url" id="copyContent">{{ url }}</span>
        <div class="w-full flex justify-between controlArea">
            <button @click="copyToClipBoard" class="
                        button
                        my-5
                        rounded
                        bg-gradient-blue-red
                        text-white
                        px-4
                        py-2
                    " v-clipboard="url">
                复制
            </button>
            <a :href="url" class="
                        button
                        my-5
                        rounded
                        bg-gradient-blue-red
                        text-white
                        px-4
                        py-2
                    ">
                导入到日历
            </a>
        </div>
    </div>

</template>
<style lang="scss" scoped>
.fit-content {
    width: fit-content;
    height: fit-content;
}


.url {
    word-wrap: break-word;
    word-break: break-all;
    max-width: 80vw;
    font-family: ui-monospace, "SF Mono", "IBM Plex Mono", "JetBrains Mono",
        "Roboto Mono", monospace;
}
</style>
<script>
export default {
    setup() { },
    data() {
        return {
            url: localStorage.getItem("url"),
        };
    },
    methods: {
        copyToClipBoard() {
            this.$toast.open({
                message: "拷贝至剪贴板成功",
                type: "success",
                position: "top",
                duration: 3000,
            });
        },
    },
};
</script>
