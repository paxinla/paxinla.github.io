Title: 迁移博客 CI 到 Github Action
Date: 2020-11-27 13:34:55
Category: 工具
Tags: github, ci
CommentId: X


当前本 blog 的 CI 是使用的 [Travis CI](https://travis-ci.org/) ，但是原 travis.org 将在 2020年12月31日转为[只读](https://docs.travis-ci.com/user/migrate/open-source-repository-migration/#frequently-asked-questions)状态，趁此时机，本博客的 CI 转而使用 Github 提供的 [Bithub Actions](https://docs.github.com/cn/free-pro-team@latest/actions) 。

<!-- PELICAN_END_SUMMARY -->


## 使用准备

- 在项目根目录下创建文件夹 `.github/workflows` 。
- 在 Github 上项目的 `Settings -> Secrets` 中设置将要在工作流定义中使用的环境变量。在本例中，我设置了 `REPO_NAME` 的值。
- 在 Github 上项目的 `Settings -> Actions` 中允许执行 Actions 工作流。


## 创建 Actions 工作流

编辑文件 `.github/workflows/gen_blog.yaml` :

```yaml
name: My Blog Github Pages

on:
  push:
    branches:
    - source

env:
  LANG: "zh_CN.UTF-8"

jobs:
  build-deploy:
    runs-on: ubuntu-18.04

    steps:
    - name: Checkout
      uses: actions/checkout@v2

    - name: Set Locale
      run: |
        sudo locale-gen zh_CN.UTF-8
        sudo update-locale LANG=zh_CN.UTF-8

    - name: Set up Python 3.7
      uses: actions/setup-python@v2
      with:
        python-version: '3.7'
        architecture: 'x64'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

    - name: Build pages
      run: |
        mkdir output
        make html
      env:
        SITEURL: ${{ secrets.REPO_NAME }}

    - name: Deploy pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./output
        publish_branch: master

```

`GITHUB_TOKEN` 是 GitHub 自动为工作流创建的 token。当需要权限认证时，可以通过 `${{ secrets.GITHUB_TOKEN}}` 在整个工作流中全局使用。


## 使用

提交并 push 项目到 Github (在我这个例子里，是推送到 source 分支)后，就可以在 Github 项目的页面上的 Actions 这个 Tab 查看 CI 的相关信息。


## 其他例子

### Release

将生成的文件或程序包放到 Release 里，如我的一个[小工具](https://github.com/paxinla/simple_netdisk):

```yaml
name: Create release wheel file

on:
  push:
    tags:
      - 'v*'

env:
  LANG: "zh_CN.UTF-8"

jobs:
  build-deploy:
    runs-on: ubuntu-18.04

    steps:
    - name: Checkout
      uses: actions/checkout@v2

    - name: Set Locale
      run: |
        sudo locale-gen zh_CN.UTF-8
        sudo update-locale LANG=zh_CN.UTF-8

    - name: Set up Python 3.7
      uses: actions/setup-python@v2
      with:
        python-version: '3.7'
        architecture: 'x64'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install wheel
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

    - name: Build whl package
      run: python setup.py bdist_wheel

    - name: Get Name of Artifact
      id: get_artifact_name
      run: |
        ARTIFACT_PATH=$(ls dist/*.whl | tail -n 1)
        ARTIFACT_NAME=$(basename ${ARTIFACT_PATH})
        echo "::set-output name=wheel_path::${ARTIFACT_PATH}"
        echo "::set-output name=wheel_name::${ARTIFACT_NAME}"
        echo "::set-output name=tag::${GITHUB_REF#refs/*/}"

    - name: Create Release
      id: create_release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: ${{ steps.get_artifact_name.outputs.tag }}
        release_name: ${{ steps.get_artifact_name.outputs.tag }}
        draft: false
        prerelease: false

    - name: Upload Release Asset
      id: upload-release-asset 
      uses: actions/upload-release-asset@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        upload_url: ${{ steps.create_release.outputs.upload_url }}
        asset_path: ./${{ steps.get_artifact_name.outputs.wheel_path }}
        asset_name: ${{ steps.get_artifact_name.outputs.wheel_name }}
        asset_content_type: application/zip
```

这里的要点是，tag 没有现成的变量可以用，从 github.ref 里提取；生成 release 的任务里，我认为 `tag_name` 最好不要用官方文档里的 github.ref ，特别是当工作流的触发条件为 branches 时；上传文件的任务里，asset 的相关值不支持 wildcard ，所以这里用了一个特别的步骤来输出待上传的文件路径和文件名。

