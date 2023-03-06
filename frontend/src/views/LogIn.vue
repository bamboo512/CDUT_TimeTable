<template>
    <div>

    </div>
    <div
        class="shadow-xl bg-white rounded-lg flex flex-col justify-between items-center dark:bg-slate-600 dark:text-white py-4 px-8 h-96 w-10/12 sm:w-8/12 md:6/12 lg:w-6/12 xl:w-120">
        <div class="w-11/12 flex flex-col justify-center items-start my-1">
            <div class="text-4xl text-gradient-blue-red font-bold my-1 ">扁舟课表</div>
            <div class="text-slate-500 text-xl font-semibold my-1 dark:text-blue-300">⚡️ 无缝同步教务处课表至日历
            </div>
        </div>
        <form @submit.prevent="onSubmit" class="flex flex-col m-0 w-11/12 ">
            <div class="my-1 flex flex-col">
                <label for="userName" class="font-bold text-lg my-1 text-slate-700 dark:text-slate-100">学号</label>
                <input type="text"
                    class="
                                                                                                                                        border border-slate-200
                                                                                                                                        rounded
                                                                                                                                        p-2
                                                                                                                                        outline-none
                                                                                                                                        focus:border-blue-400 focus:border-1 focus:bg-white
                                                                                                                                    "
                    id="userName" v-model="userName" placeholder="你的学号" />
            </div>

            <div class="flex flex-col my-1">
                <label for="password" class="font-bold text-lg my-1 text-slate-700 dark:text-slate-100">密码</label>
                <input type="password" class="border border-slate-200 rounded p-2 outline-none" id="password"
                    v-model="password" placeholder="你的新教务处密码" />
            </div>

            <!-- <div class="flex flex-col my-1">
                <label for="captcha" class="font-bold text-lg my-1 text-slate-700 dark:text-slate-100">密码</label>
                <input type="text" class="border border-slate-200 rounded p-2 outline-none" id="password"
                    v-model="captcha" placeholder="输入验证码（不区分大小写）" />
                <img :src="https://jw.cdut.edu.cn/verifycode.servlet?t=0" alt="验证码" class="w-32 h-16 mt-2" />
            </div> -->
            <button type="submit" class="mt-6 mb-4 rounded-lg bg-gradient-blue-red text-white font-bold w-full p-2">
                登录
            </button>
        </form>
    </div>
</template>
<style lang="scss" >
.bg-gradient-blue-red {
    background: linear-gradient(120deg, #4b74dacc, #4b74daa0, #da554b50);
}
</style>
<script>
export default {
    setup() {

    },
    data() {
        return {
            userName: null,
            password: null,

        };
    },
    methods: {
        onSubmit() {
            let userName = this.userName;
            let password = this.password;

            // ! 表单验证
            let validateMessage = "";
            if (!userName) {
                validateMessage += "学号不能为空<br/>";
            }

            if (!password) {
                validateMessage += "密码不能为空<br/>";
            }

            if (userName && !/^[f,F]{0,1}\d{12}$/.test(userName)) {
                validateMessage += "学号格式不正确<br/>";
            }
            if (userName && !/^.{6,32}$/.test(password)) {
                validateMessage += "密码格式不正确<br/>";
            }
            if (validateMessage) {
                this.$toast.open({
                    message: validateMessage,
                    type: "error",
                    duration: 3000,
                });
                return;
            }


            // ! 提交 

            let url = this.$store.state.backendUrl + "/api/signup";

            let payload = {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    userName: userName,
                    password: password,
                }),
            };

            // ! 发送注册请求
            fetch(url, payload)
                .then((response) => response.json())
                .then((data) => {
                    console.log(data);
                    if (data.code === 0) {
                        // ! 注册成功
                        this.$toast.open({
                            message: "登录成功",
                            type: "success",
                            duration: 3000,
                        });
                        localStorage.setItem("url", data.url);

                        this.$router.push("/Response");
                    } else if (data.code === -1) {
                        // ! 登录失败：密码或学号错误

                        this.$toast.open({
                            message: "登录失败：新教务处密码或学号错误",
                            type: "error",
                            duration: 3000,
                        });
                    } else if (data.code === -2) {
                        // ! 登录失败：无法将用户信息写入数据库

                        this.$toast.open({
                            message: "登录失败：无法将用户信息写入数据库",
                            type: "error",
                            duration: 3000,
                        });
                    }
                })
                .catch(() => {
                    // ! 注册失败：未知错误
                    this.$toast.open({
                        message: "登录失败：可能是服务器原因。",
                        type: "error",
                        duration: 3000,
                    });
                });
        },
    },
};
</script>
