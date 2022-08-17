雑メモ

PSDDividerでやってること
* PSDファイル読み込み
* PSDを階層ごとに画像出力
* PSDの情報とレイヤーの情報をjson出力

SettingCreatorでやってること
* 画像一式とPSDレイヤー情報のjson取得
* 良い感じに読み込んでsetting作成
* settingを指定のフォルダに出力

-------------------------

jsonファイルの読み込みについて（同フォルダにサンプルあり）
* psd_layer_info.json
  * レイヤーの情報を連番にして並べたの、レイヤーサイズとか色々入っている
  * 順番が速い方がレイヤーとして一番背面に来る
  * depend_group_listは属しているグループ、グループの先頭に来る奴だけが持ってる。
  * setting作る際も若い番号から順に取得していく
  * いずれ「exist_!」とか「exist_*」とか属性追加してPSDToolの独自機能対応できたら嬉しいな、夢物語

* psd_original_info.json
  * PSD全体の情報、PSDのサイズとかレイヤー数とか、今はそれだけ

-------------------------

settingの出力先

C:\ProgramData\Blackmagic Design\DaVinci Resolve\Fusion\Templates\Edit\Generators
