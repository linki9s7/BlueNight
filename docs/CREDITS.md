# クレジットと使用素材のライセンス

ゲームのスタッフロール・配布物に、以下の表記を入れること。

## 音源

| 素材 | 作者 | ライセンス | 使っている場所 |
| --- | --- | --- | --- |
| MuseScore General SoundFont | S. Christian Collins | MIT | すべての BGM の楽器 |
| 雨の録音 | Mike Koenig（soundbible.com。2014 年に Dawid Gan が切り出し） | CC BY 3.0（表記が必要） | 環境音「雨」 |
| 川の録音 | Adam Newns（vennaudio.com） | CC0（表記不要） | 環境音「雨」「波」 |
| 滝の録音 | Leonard "VKProduktion" Graf | CC0（表記不要） | 環境音「波」「遠くのハイウェイ」 |
| 風・葉のそよぎの録音 | Wildfire Games（0 A.D.） | CC BY-SA 3.0（表記が必要・継承あり） | 環境音「遠くのハイウェイ」「夜の虫」 |

- 環境音の録音は Ubuntu の `supertuxkart-data` パッケージから取り出した（同パッケージの copyright ファイルにライセンス記載）。
  詳細は `Tools/Music/sources/README.md`。
- 表記例：`Rain recording by Mike Koenig (soundbible.com), licensed under CC BY 3.0`
- 表記例：`Wind recordings from 0 A.D. by Wildfire Games, licensed under CC BY-SA 3.0`
- `ambient_highway.ogg` と `ambient_crickets.ogg` は CC BY-SA 3.0 の素材を含むため、同じ CC BY-SA 3.0 で提供する。

## フォント

| 素材 | 作者 | ライセンス |
| --- | --- | --- |
| DotGothic16 | The DotGothic16 Project Authors（Fontworks） | SIL Open Font License 1.1（`Assets/008_Fonts/DotGothic16-OFL.txt` を同梱） |

## 使わないと判断したもの

| 素材 | 理由 |
| --- | --- |
| tonejs-instruments（npm の `tonejs-instrument-*`） | 録音の出どころとライセンスが記載されておらず、商用での利用可否を確認できないため |
| Salamander Grand Piano V3（Alexander Holm、CC BY 3.0） | ライセンスは問題ないが、リズムに合わせて低音が「ドシン」と響くのが不快とのユーザー判断 |
| 0 A.D. の波・雨の録音（Wildfire Games、CC BY-SA 3.0） | 雨と波は CC0／CC BY の素材で作った今の版をユーザーが気に入ったため使わない（風と葉の音だけ、ハイウェイと虫に使う） |
