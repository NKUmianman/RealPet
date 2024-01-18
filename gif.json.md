```json
{
    "start": [ // 开始动画
    // 可以直接填路径
    // 也可以填对象
        "./petGif/StartUp/Happy_1/Happy_1.gif",
        "./petGif/StartUp/Happy/Happy.gif",
        {
            "path": "./petGif/StartUp/PoorCondition/PoorCondition.gif", // 路径 必填
            "time": [[0, 6], [21, 24]], // 显示时间段，选填，24小时制 可选值：0~24，小在前，大在后，默认值：[[0, 24]]
            "force": true // 在此时间段是否强制显示这个动画，选填，默认值：false
        }
    ],
    "default": [ // 默认动画
    // 可以直接填路径
    // 也可以填对象
        "./petGif/StartUp/Happy_1/Happy_1.gif",
        {
            "id": "group1", // id 可以指明调用这个动画 选填 默认值：none
            "group": true, // 是否是动画组
            "paths": [
                "./petGif/Default/Happy/1/1.gif",
                "./petGif/Default/Happy/2/2.gif",
                "./petGif/Default/Happy/3/3.gif"
            ], // 动画组的gif
            "orderId": "defaultHappy", // 动画组id，在后面设置的，group=true必填
            "weight": 90 // 权重 整数 默认是10 不能小于0
        },
        {
            "path": "./petGif/StartUp/Happy/Happy.gif",
            "weight": 1, // 同上
            "time": [[0, 6], [21, 24]], // 同上
            "force": true // 同上
        },
        { // 同default
            "time": [[0, 6], [23, 24]], // 这段时间出现
            "group": true,
            "paths": [
                "./petGif/Sleep/A_Happy/A_Happy.gif",
                "./petGif/Sleep/B_Happy/B_Happy.gif",
                "./petGif/Sleep/C_Happy/C_Happy.gif"
            ],
            "orderId": "sleepHappy"
        },
        {
            "time": [[7, 8], [12, 13], [17, 18]],
            "path": "./petGif/Eat/Happy/back_lay/back_lay.gif",
            "interrupt": false // 动画是否允许被打断，动画组暂时不能用
        }
    ],
    "touch": [ // 同default
        "./petGif/Touch_Body/A_Happy/tb2/tb2.gif"
    ],
    "move": [ // 同default
        "./petGif/Raise/Raised_Dynamic/Nomal/2/2.gif"
    ],
    "say": [ // 同default
        "./petGif/Raise/Raised_Dynamic/Nomal/2/2.gif"
    ],
    "orders": {
        "defaultHappy": [ // 必须和上面的orderId一样
            {
                "i": 0, // 路径下标，必填
                "amount": 1 // 执行次数，选填
            },
            {
                "i": 1,
                "time": [2000, 5000] // 2s到5s的随机时长
            },
            {
                "i": 2,
                "amount": 1
            },
            {
                "i": 1,
                "time": [2000, 4000]
            },
            {
                "i": 0,
                "amount": 1
            },
            {
                "i": 1,
                "time": [5000, 10000]
            }
        ],
        "sleepHappy": [
            {
                "i": 0,
                "amount": 1
            },
            {
                "i": 1,
                "time": 15000 // 时长超过15s
            },
            {
                "i": 2,
                "amount": 1,
                "interrupt": false, // 动画执行时是否允许被打断，默认值：true
                "exit": true // 退出动画组时，必须执行的动画，默认值false
            }
        ]
    }
}
```