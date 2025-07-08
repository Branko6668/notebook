document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');

    // 设置 canvas 尺寸为窗口大小
    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    // 可配置参数
    const config = {
        fishCount: 10,  // 鱼的数量
        colors: [
            '#98FF98', '#FFC0CB', // 薄荷绿 & 浅粉红
            '#D8BFD8', '#FFFFE0', // 浅紫色 & 浅黄色
            '#ADD8E6', '#F08080', // 浅蓝色 & 柔和珊瑚色
            '#FFC1CC', '#FFDAB9', // 浅玫瑰色 & 浅橙色
            '#E6E6FA', '#F3E5AB', // 薰衣草色 & 香草色
            '#FF6B6B', '#4ECDC4', // 鱼的颜色
            '#45B7D1', '#96CEB4', // 鱼的颜色
            '#FFEEAD', '#D4A5A5', // 鱼的颜色
            '#FFC0CB', '#FFD700', // 粉红色 & 金色
            '#FFA07A', '#90EE90', // 浅珊瑚色 & 淡绿色
            '#FF6347', '#E6E6FA', // 番茄色 & 薰衣草色
            '#FF69B4', '#8A2BE2', // 热粉色 & 蓝紫色
            '#00FA9A', '#DDA0DD', // 绿松石色 & 李子色
            '#FF4500', '#2E8B57', // 橙红色 & 海绿色
            '#DAA520', '#BA55D3', // 金麒麟色 & 中兰花紫
            '#CD5C5C', '#87CEEB', // 印度红 & 天空蓝
            '#20B2AA', '#778899', // 浅海绿色 & 浅灰色
            '#B0E0E6'             // 粉蓝色
        ]
    };

    // 随机排序颜色数组
    config.colors.sort(() => Math.random() - 0.5);

    // 从 localStorage 获取上次鼠标位置
    let mouseX = parseFloat(localStorage.getItem('lastMouseX')) || window.innerWidth / 2;
    let mouseY = parseFloat(localStorage.getItem('lastMouseY')) || window.innerHeight / 2;

    class Fish {
        constructor(index) {
            this.x = mouseX;
            this.y = mouseY;
            this.angle = Math.random() * Math.PI * 0.01;
            this.radius = 30 + Math.random() * 60; // 最小半径，随机误差范围
            this.speed = 0.01 + Math.random() * 0.03; // 最小速度，随机速度范围
            this.size = 4 + Math.random() * 3; // 相对尺寸
            this.color = config.colors[index % config.colors.length];
            this.offset = Math.random() * Math.PI * 20; // 初始分散程度
            this.targetX = this.x;
            this.targetY = this.y;
        }

        update() {
            // 计算目标位置
            if (this.prevMouseX !== mouseX || this.prevMouseY !== mouseY) {
                // 鼠标移动时，跟随鼠标
                this.targetX = mouseX;
                this.targetY = mouseY;
            } else {
                // 鼠标静止时，计算围绕位置
                this.angle += this.speed;
                this.targetX = mouseX + Math.cos(this.angle + this.offset) * this.radius;
                this.targetY = mouseY + Math.sin(this.angle + this.offset) * this.radius;
            }

            // 平滑移动到目标位置
            const dx = this.targetX - this.x;
            const dy = this.targetY - this.y;
            this.x += dx * 0.1;
            this.y += dy * 0.1;

            this.prevMouseX = mouseX;
            this.prevMouseY = mouseY;
        }

        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fillStyle = this.color;
            ctx.fill();
            ctx.shadowColor = this.color;
            ctx.shadowBlur = 15;
        }
    }

    const fish = [];

    // 初始化鱼群
    for (let i = 0; i < config.fishCount; i++) {
        fish.push(new Fish(i));
    }

    // 更新鼠标位置
    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });

    // 动画循环
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        fish.forEach(f => {
            f.update();
            f.draw();
        });

        requestAnimationFrame(animate);
    }

    animate();
});
