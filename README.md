# 网站接口模块说明

## 环境要求

需要 `Python3.7` （3.7.7 更好）。

需要额外安装 `pynvml` 模块。

## 用法示例

`web_interface` 模块中实现了 `WebInterface` 类，通过这个类的方法可以向网站后端发送数据。

**使用 `web_interface` 模块前请确保你的训练程序能良好运行，避免运行过程中报错导致数据滞留在网站后端数据库。**

```python
# 新建一个 `WebInterface` 类的对象，需要传入当前训练程序的名称（名称自定义，要避免容易重复的名称，建议使用自己的姓名拼音缩写加训练程序名称）。
web_interface = WebInterface(training_name = "test")

# 注册当前训练程序的信息到网站后端，需要传入当前训练程序所使用的 GPU 的索引号（整数），需要注意的是应当传入一个 `list` （即使只有一个 GPU 索引）。
used_gpu_indexes = list()
used_gpu_indexes.append(0)
is_successful = web_interface.register(used_gpu_indexes)

# `WebInterface` 类的方法返回一个 `bool` 值以表示是否成功，如果不成功需要做出相应的措施（如重试）。
if is_successful is False:
    print("Failed to register.")

# 推送训练过程中的数据，需要传入一个 `dict` ，其中的的键值对一般为 `loss` 、 `accuracy` 、 `val_loss` 、 `val_accuracy` （可以自定义）。
data = {"loss": 0.01, "accuracy": 0.99, "val_loss": 0.01, "val_accuracy": 0.99}
is_successful = web_interface.publish(data)

if is_successful is False:
    print("Failed to publish.")

# 注销当前训练程序，训练结束前应当注销。
is_successful = web_interface.logout()

if is_successful is False:
    print("Failed to logout.")

```
