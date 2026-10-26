# ドット絵の点検結果

`python3 Tools/Art/pixel_check.py` で更新する。ダブりの目安は 10 以下。

数字は機械的な候補。目で確かめて直さないと決めたものは「確認済み」に理由を書く（`REVIEWED`）。

| 絵 | 色数 | パレット外 | ダブり | バンディング（帯/ドット） | 浮いた AA 候補 | ノイズ % | 網点 % | 光の向きが逆の系統 | 確認済み |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Buildings/bus_shelter.png | 10 |  | 0 | 0/0 | 0 | 0.0 | 0.0 | stone | 光の向き：建物は屋根・壁・窓・基礎で素材が違い、系統全体の重心では判断できない（部品ごとに左上の光を確認済み）。窓の明かりは光源なので陰影の向きとは関係ない |
| Buildings/grandma_shop.png | 21 |  | 0 | 0/0 | 1 | 0.0 | 0.0 | brown, red, warm | 光の向き：建物は屋根・壁・窓・基礎で素材が違い、系統全体の重心では判断できない（部品ごとに左上の光を確認済み）。窓の明かりは光源なので陰影の向きとは関係ない |
| Buildings/house.png | 13 |  | 0 | 0/0 | 0 | 0.0 | 0.0 | stone | 光の向き：建物は屋根・壁・窓・基礎で素材が違い、系統全体の重心では判断できない（部品ごとに左上の光を確認済み）。窓の明かりは光源なので陰影の向きとは関係ない |
| Buildings/lamp_shop.png | 15 |  | 0 | 0/0 | 3 | 0.1 | 0.0 | brown, warm | 光の向き：建物は屋根・壁・窓・基礎で素材が違い、系統全体の重心では判断できない（部品ごとに左上の光を確認済み）。窓の明かりは光源なので陰影の向きとは関係ない |
| Buildings/shutter_shop_0.png | 10 |  | 0 | 0/0 | 0 | 0.0 | 0.0 | stone, night | 光の向き：建物は屋根・壁・窓・基礎で素材が違い、系統全体の重心では判断できない（部品ごとに左上の光を確認済み）。窓の明かりは光源なので陰影の向きとは関係ない |
| Buildings/shutter_shop_1.png | 12 |  | 0 | 0/0 | 0 | 0.0 | 0.0 | brown | 光の向き：建物は屋根・壁・窓・基礎で素材が違い、系統全体の重心では判断できない（部品ごとに左上の光を確認済み）。窓の明かりは光源なので陰影の向きとは関係ない |
| Characters/Cat/cat_idle_0.png | 6 |  | 0 | 0/0 | 0 | 2.9 | 0.0 |  |  |
| Characters/Cat/cat_idle_1.png | 5 |  | 0 | 0/0 | 0 | 1.0 | 0.0 |  |  |
| Characters/Cat/cat_idle_2.png | 6 |  | 0 | 0/0 | 0 | 3.0 | 0.0 |  |  |
| Characters/Cat/cat_idle_3.png | 6 |  | 0 | 0/0 | 0 | 2.9 | 0.0 |  |  |
| Characters/Grandma/grandma_idle_0.png | 12 |  | 0 | 1/4 | 1 | 1.9 | 0.0 |  | あごの肌の帯は口まわりの形。2 コマ目の右肩の影は手との境目 |
| Characters/Grandma/grandma_idle_1.png | 12 |  | 0 | 2/7 | 1 | 1.9 | 0.0 |  | あごの肌の帯は口まわりの形。2 コマ目の右肩の影は手との境目 |
| Characters/Keeper/keeper_idle_0.png | 14 |  | 0 | 4/14 | 0 | 1.8 | 0.0 |  | 顔の帯（めがね・口ひげ・鼻のまわり）は形の細部で、陰影の帯ではない |
| Characters/Keeper/keeper_idle_1.png | 14 |  | 0 | 4/13 | 0 | 2.2 | 0.0 |  | 顔の帯（めがね・口ひげ・鼻のまわり）は形の細部で、陰影の帯ではない |
| Characters/Nemu/nemu_fly_0.png | 9 |  | 0 | 6/33 | 0 | 4.0 | 0.0 | warm | オオミズアオの模様（前羽の赤茶の帯・目玉模様・尾の先の黄色）と細い体は模様・形で、陰影の帯ではない |
| Characters/Nemu/nemu_fly_1.png | 9 |  | 0 | 2/8 | 4 | 5.4 | 0.0 |  | オオミズアオの模様（前羽の赤茶の帯・目玉模様・尾の先の黄色）と細い体は模様・形で、陰影の帯ではない |
| Characters/Nemu/nemu_fly_2.png | 9 |  | 0 | 6/33 | 0 | 4.0 | 0.0 | warm | オオミズアオの模様（前羽の赤茶の帯・目玉模様・尾の先の黄色）と細い体は模様・形で、陰影の帯ではない |
| Characters/Nemu/nemu_fly_3.png | 9 |  | 0 | 6/29 | 2 | 5.0 | 0.0 |  | オオミズアオの模様（前羽の赤茶の帯・目玉模様・尾の先の黄色）と細い体は模様・形で、陰影の帯ではない |
| Characters/Ruri/ruri_idle_down_0.png | 16 |  | 0 | 1/3 | 1 | 1.8 | 0.0 |  | 顔の肌の帯（目と髪のあいだ・あご）、口・マフラーのつや・靴のつやの点は形の細部で、陰影の帯や AA ではない |
| Characters/Ruri/ruri_idle_down_1.png | 16 |  | 0 | 1/3 | 1 | 1.8 | 0.0 |  | 顔の肌の帯（目と髪のあいだ・あご）、口・マフラーのつや・靴のつやの点は形の細部で、陰影の帯や AA ではない |
| Characters/Ruri/ruri_idle_down_2.png | 16 |  | 0 | 1/3 | 1 | 1.2 | 0.0 |  | 顔の肌の帯（目と髪のあいだ・あご）、口・マフラーのつや・靴のつやの点は形の細部で、陰影の帯や AA ではない |
| Characters/Ruri/ruri_idle_down_3.png | 16 |  | 0 | 1/3 | 1 | 1.8 | 0.0 |  | 顔の肌の帯（目と髪のあいだ・あご）、口・マフラーのつや・靴のつやの点は形の細部で、陰影の帯や AA ではない |
| Characters/Ruri/ruri_idle_left_0.png | 16 |  | 0 | 0/0 | 6 | 2.6 | 0.0 |  | 顔の肌の帯（目と髪のあいだ・あご）、口・マフラーのつや・靴のつやの点は形の細部で、陰影の帯や AA ではない |
| Characters/Ruri/ruri_idle_left_1.png | 16 |  | 0 | 0/0 | 6 | 2.6 | 0.0 |  | 顔の肌の帯（目と髪のあいだ・あご）、口・マフラーのつや・靴のつやの点は形の細部で、陰影の帯や AA ではない |
| Characters/Ruri/ruri_idle_left_2.png | 16 |  | 0 | 0/0 | 6 | 2.6 | 0.0 |  | 顔の肌の帯（目と髪のあいだ・あご）、口・マフラーのつや・靴のつやの点は形の細部で、陰影の帯や AA ではない |
| Characters/Ruri/ruri_idle_left_3.png | 16 |  | 0 | 0/0 | 6 | 2.6 | 0.0 |  | 顔の肌の帯（目と髪のあいだ・あご）、口・マフラーのつや・靴のつやの点は形の細部で、陰影の帯や AA ではない |
| Characters/Ruri/ruri_idle_right_0.png | 17 |  | 0 | 0/0 | 3 | 1.6 | 0.0 |  | 顔の肌の帯（目と髪のあいだ・あご）、口・マフラーのつや・靴のつやの点は形の細部で、陰影の帯や AA ではない |
| Characters/Ruri/ruri_idle_right_1.png | 17 |  | 0 | 0/0 | 3 | 1.6 | 0.0 |  | 顔の肌の帯（目と髪のあいだ・あご）、口・マフラーのつや・靴のつやの点は形の細部で、陰影の帯や AA ではない |
| Characters/Ruri/ruri_idle_right_2.png | 17 |  | 0 | 0/0 | 3 | 1.6 | 0.0 |  | 顔の肌の帯（目と髪のあいだ・あご）、口・マフラーのつや・靴のつやの点は形の細部で、陰影の帯や AA ではない |
| Characters/Ruri/ruri_idle_right_3.png | 17 |  | 0 | 0/0 | 3 | 1.6 | 0.0 |  | 顔の肌の帯（目と髪のあいだ・あご）、口・マフラーのつや・靴のつやの点は形の細部で、陰影の帯や AA ではない |
| Characters/Ruri/ruri_idle_up_0.png | 15 |  | 0 | 0/0 | 1 | 1.5 | 0.0 |  | 顔の肌の帯（目と髪のあいだ・あご）、口・マフラーのつや・靴のつやの点は形の細部で、陰影の帯や AA ではない |
| Characters/Ruri/ruri_idle_up_1.png | 15 |  | 0 | 0/0 | 1 | 1.5 | 0.0 |  | 顔の肌の帯（目と髪のあいだ・あご）、口・マフラーのつや・靴のつやの点は形の細部で、陰影の帯や AA ではない |
| Characters/Ruri/ruri_idle_up_2.png | 15 |  | 0 | 0/0 | 1 | 0.9 | 0.0 |  | 顔の肌の帯（目と髪のあいだ・あご）、口・マフラーのつや・靴のつやの点は形の細部で、陰影の帯や AA ではない |
| Characters/Ruri/ruri_idle_up_3.png | 15 |  | 0 | 0/0 | 1 | 1.5 | 0.0 |  | 顔の肌の帯（目と髪のあいだ・あご）、口・マフラーのつや・靴のつやの点は形の細部で、陰影の帯や AA ではない |
| Characters/Ruri/ruri_walk_down_0.png | 16 |  | 0 | 1/3 | 1 | 1.8 | 0.0 |  | 顔の肌の帯（目と髪のあいだ・あご）、口・マフラーのつや・靴のつやの点は形の細部で、陰影の帯や AA ではない |
| Characters/Ruri/ruri_walk_down_1.png | 16 |  | 0 | 1/3 | 1 | 1.2 | 0.0 |  | 顔の肌の帯（目と髪のあいだ・あご）、口・マフラーのつや・靴のつやの点は形の細部で、陰影の帯や AA ではない |
| Characters/Ruri/ruri_walk_down_2.png | 16 |  | 0 | 1/3 | 1 | 1.8 | 0.0 |  | 顔の肌の帯（目と髪のあいだ・あご）、口・マフラーのつや・靴のつやの点は形の細部で、陰影の帯や AA ではない |
| Characters/Ruri/ruri_walk_down_3.png | 16 |  | 0 | 1/3 | 1 | 1.2 | 0.0 |  | 顔の肌の帯（目と髪のあいだ・あご）、口・マフラーのつや・靴のつやの点は形の細部で、陰影の帯や AA ではない |
| Characters/Ruri/ruri_walk_left_0.png | 17 |  | 0 | 0/0 | 6 | 3.0 | 0.0 | stone | 顔の肌の帯（目と髪のあいだ・あご）、口・マフラーのつや・靴のつやの点は形の細部で、陰影の帯や AA ではない ／ 靴下の光の向き：奥の脚を暗くしているのは奥行きの表現 |
| Characters/Ruri/ruri_walk_left_1.png | 16 |  | 0 | 0/0 | 6 | 2.6 | 0.0 |  | 顔の肌の帯（目と髪のあいだ・あご）、口・マフラーのつや・靴のつやの点は形の細部で、陰影の帯や AA ではない |
| Characters/Ruri/ruri_walk_left_2.png | 17 |  | 0 | 0/0 | 6 | 2.7 | 0.0 |  | 顔の肌の帯（目と髪のあいだ・あご）、口・マフラーのつや・靴のつやの点は形の細部で、陰影の帯や AA ではない |
| Characters/Ruri/ruri_walk_left_3.png | 16 |  | 0 | 0/0 | 6 | 2.6 | 0.0 |  | 顔の肌の帯（目と髪のあいだ・あご）、口・マフラーのつや・靴のつやの点は形の細部で、陰影の帯や AA ではない |
| Characters/Ruri/ruri_walk_right_0.png | 18 |  | 0 | 0/0 | 4 | 1.8 | 0.0 | stone | 顔の肌の帯（目と髪のあいだ・あご）、口・マフラーのつや・靴のつやの点は形の細部で、陰影の帯や AA ではない ／ 靴下の光の向き：奥の脚を暗くしているのは奥行きの表現 |
| Characters/Ruri/ruri_walk_right_1.png | 17 |  | 0 | 0/0 | 3 | 1.6 | 0.0 |  | 顔の肌の帯（目と髪のあいだ・あご）、口・マフラーのつや・靴のつやの点は形の細部で、陰影の帯や AA ではない |
| Characters/Ruri/ruri_walk_right_2.png | 18 |  | 0 | 0/0 | 2 | 1.5 | 0.0 |  | 顔の肌の帯（目と髪のあいだ・あご）、口・マフラーのつや・靴のつやの点は形の細部で、陰影の帯や AA ではない |
| Characters/Ruri/ruri_walk_right_3.png | 17 |  | 0 | 0/0 | 3 | 1.6 | 0.0 |  | 顔の肌の帯（目と髪のあいだ・あご）、口・マフラーのつや・靴のつやの点は形の細部で、陰影の帯や AA ではない |
| Characters/Ruri/ruri_walk_up_0.png | 15 |  | 0 | 0/0 | 1 | 1.5 | 0.0 |  | 顔の肌の帯（目と髪のあいだ・あご）、口・マフラーのつや・靴のつやの点は形の細部で、陰影の帯や AA ではない |
| Characters/Ruri/ruri_walk_up_1.png | 15 |  | 0 | 0/0 | 1 | 0.9 | 0.0 |  | 顔の肌の帯（目と髪のあいだ・あご）、口・マフラーのつや・靴のつやの点は形の細部で、陰影の帯や AA ではない |
| Characters/Ruri/ruri_walk_up_2.png | 15 |  | 0 | 0/0 | 1 | 1.5 | 0.0 |  | 顔の肌の帯（目と髪のあいだ・あご）、口・マフラーのつや・靴のつやの点は形の細部で、陰影の帯や AA ではない |
| Characters/Ruri/ruri_walk_up_3.png | 15 |  | 0 | 0/0 | 1 | 0.9 | 0.0 |  | 顔の肌の帯（目と髪のあいだ・あご）、口・マフラーのつや・靴のつやの点は形の細部で、陰影の帯や AA ではない |
| Characters/Shadows/shadow_cat_0.png | 4 |  | 0 | 0/0 | 0 | 1.3 | 0.0 |  |  |
| Characters/Shadows/shadow_cat_1.png | 3 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Characters/Shadows/shadow_cat_2.png | 4 |  | 0 | 0/0 | 0 | 1.3 | 0.0 |  |  |
| Characters/Shadows/shadow_cat_3.png | 4 |  | 0 | 0/0 | 0 | 1.3 | 0.0 |  |  |
| Characters/Shadows/shadow_grandma_0.png | 3 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Characters/Shadows/shadow_grandma_1.png | 3 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Characters/Shadows/shadow_grandma_2.png | 3 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Characters/Shadows/shadow_grandma_3.png | 3 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Characters/Shadows/shadow_ruri_idle_down_0.png | 4 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Characters/Shadows/shadow_ruri_idle_down_1.png | 4 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Characters/Shadows/shadow_ruri_idle_down_2.png | 4 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Characters/Shadows/shadow_ruri_idle_down_3.png | 4 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Characters/Shadows/shadow_ruri_idle_left_0.png | 4 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Characters/Shadows/shadow_ruri_idle_left_1.png | 4 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Characters/Shadows/shadow_ruri_idle_left_2.png | 4 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Characters/Shadows/shadow_ruri_idle_left_3.png | 4 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Characters/Shadows/shadow_ruri_idle_right_0.png | 4 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Characters/Shadows/shadow_ruri_idle_right_1.png | 4 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Characters/Shadows/shadow_ruri_idle_right_2.png | 4 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Characters/Shadows/shadow_ruri_idle_right_3.png | 4 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Characters/Shadows/shadow_ruri_idle_up_0.png | 3 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Characters/Shadows/shadow_ruri_idle_up_1.png | 3 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Characters/Shadows/shadow_ruri_idle_up_2.png | 3 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Characters/Shadows/shadow_ruri_idle_up_3.png | 3 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Characters/Shadows/shadow_ruri_walk_down_0.png | 4 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Characters/Shadows/shadow_ruri_walk_down_1.png | 4 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Characters/Shadows/shadow_ruri_walk_down_2.png | 4 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Characters/Shadows/shadow_ruri_walk_down_3.png | 4 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Characters/Shadows/shadow_ruri_walk_left_0.png | 4 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Characters/Shadows/shadow_ruri_walk_left_1.png | 4 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Characters/Shadows/shadow_ruri_walk_left_2.png | 4 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Characters/Shadows/shadow_ruri_walk_left_3.png | 4 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Characters/Shadows/shadow_ruri_walk_right_0.png | 4 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Characters/Shadows/shadow_ruri_walk_right_1.png | 4 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Characters/Shadows/shadow_ruri_walk_right_2.png | 4 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Characters/Shadows/shadow_ruri_walk_right_3.png | 4 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Characters/Shadows/shadow_ruri_walk_up_0.png | 3 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Characters/Shadows/shadow_ruri_walk_up_1.png | 3 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Characters/Shadows/shadow_ruri_walk_up_2.png | 3 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Characters/Shadows/shadow_ruri_walk_up_3.png | 3 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Faces/face_grandma_normal.png | 8 |  | 0 | 1/3 | 0 | 0.1 | 0.0 |  | 目・口・めがね・口ひげなどの顔の細部（形の線）は陰影の帯ではない |
| Faces/face_grandma_smile.png | 8 |  | 0 | 1/3 | 0 | 0.1 | 0.0 |  | 目・口・めがね・口ひげなどの顔の細部（形の線）は陰影の帯ではない |
| Faces/face_grandma_teary.png | 9 |  | 0 | 1/3 | 1 | 0.2 | 0.0 |  | 目・口・めがね・口ひげなどの顔の細部（形の線）は陰影の帯ではない |
| Faces/face_keeper_normal.png | 11 |  | 0 | 4/16 | 1 | 0.2 | 0.0 |  | 目・口・めがね・口ひげなどの顔の細部（形の線）は陰影の帯ではない |
| Faces/face_keeper_smile.png | 11 |  | 0 | 4/16 | 1 | 0.2 | 0.0 |  | 目・口・めがね・口ひげなどの顔の細部（形の線）は陰影の帯ではない |
| Faces/face_nemu_happy.png | 11 |  | 0 | 20/87 | 10 | 0.7 | 0.0 | warm | 目・口・めがね・口ひげなどの顔の細部（形の線）は陰影の帯ではない ／ 目玉模様の縁・羽の筋・触角の羽毛・前羽の帯は模様で、陰影の帯ではない |
| Faces/face_nemu_normal.png | 11 |  | 0 | 24/101 | 10 | 0.9 | 0.0 | warm | 目・口・めがね・口ひげなどの顔の細部（形の線）は陰影の帯ではない ／ 目玉模様の縁・羽の筋・触角の羽毛・前羽の帯は模様で、陰影の帯ではない |
| Faces/face_nemu_sleepy.png | 11 |  | 0 | 21/92 | 10 | 0.7 | 0.0 | warm | 目・口・めがね・口ひげなどの顔の細部（形の線）は陰影の帯ではない ／ 目玉模様の縁・羽の筋・触角の羽毛・前羽の帯は模様で、陰影の帯ではない |
| Faces/face_nemu_surprised.png | 11 |  | 0 | 21/90 | 10 | 0.9 | 0.0 | warm | 目・口・めがね・口ひげなどの顔の細部（形の線）は陰影の帯ではない ／ 目玉模様の縁・羽の筋・触角の羽毛・前羽の帯は模様で、陰影の帯ではない |
| Faces/face_ruri_gentle.png | 13 |  | 0 | 1/3 | 1 | 0.1 | 0.0 |  | 目・口・めがね・口ひげなどの顔の細部（形の線）は陰影の帯ではない |
| Faces/face_ruri_normal.png | 14 |  | 0 | 1/3 | 1 | 0.2 | 0.0 |  | 目・口・めがね・口ひげなどの顔の細部（形の線）は陰影の帯ではない |
| Faces/face_ruri_sad.png | 14 |  | 0 | 1/3 | 1 | 0.2 | 0.0 |  | 目・口・めがね・口ひげなどの顔の細部（形の線）は陰影の帯ではない |
| Faces/face_ruri_smile.png | 14 |  | 0 | 4/12 | 1 | 0.2 | 0.0 |  | 目・口・めがね・口ひげなどの顔の細部（形の線）は陰影の帯ではない |
| Faces/face_ruri_surprised.png | 15 |  | 0 | 6/29 | 1 | 0.2 | 0.0 |  | 目・口・めがね・口ひげなどの顔の細部（形の線）は陰影の帯ではない |
| Props/a_sign.png | 4 |  | 0 | 1/3 | 0 | 0.0 | 0.0 |  | 黒板のチョークの線は模様 |
| Props/beer_crates.png | 4 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Props/bench.png | 5 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Props/bicycle.png | 5 |  | 0 | 0/0 | 0 | 0.7 | 0.0 |  |  |
| Props/bus_sign.png | 7 |  | 0 | 0/0 | 0 | 1.3 | 0.0 |  |  |
| Props/curve_mirror.png | 5 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Props/extinguisher_box.png | 5 |  | 0 | 0/0 | 0 | 1.1 | 0.0 |  |  |
| Props/hook.png | 4 |  | 0 | 0/0 | 0 | 1.1 | 0.0 |  |  |
| Props/lamp.png | 5 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Props/lantern.png | 4 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Props/mailbox.png | 6 |  | 0 | 1/3 | 0 | 0.0 | 0.0 |  | 差し入れ口の上の明るい点はつやの模様 |
| Props/pot_plant.png | 6 |  | 0 | 0/0 | 1 | 2.4 | 0.0 |  | 花の 1 ドットは模様（AA ではない） |
| Props/power_pole.png | 8 |  | 0 | 1/4 | 0 | 0.6 | 0.0 | stone | 光の向き：足元の黄色と黒の巻き標識はしま模様で、陰影ではない |
| Props/puddle_moon.png | 5 |  | 0 | 0/0 | 0 | 0.0 | 0.0 | night | 光の向き：水面の揺らぎ（明るい線）は映り込みで、陰影ではない |
| Props/trash_bin.png | 4 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Props/vending.png | 10 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Tiles/block_wall.png | 3 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Tiles/block_wall_top.png | 3 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Tiles/crosswalk.png | 4 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Tiles/crosswalk_0.png | 3 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Tiles/crosswalk_1.png | 3 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Tiles/curb.png | 6 |  | 0 | 0/0 | 0 | 0.8 | 0.0 |  |  |
| Tiles/drain.png | 5 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Tiles/drain_0.png | 5 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Tiles/drain_1.png | 4 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Tiles/manhole.png | 4 |  | 0 | 3/12 | 0 | 0.0 | 0.0 |  | ふたの格子は模様 |
| Tiles/overlay_cast_shadow.png | 1 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Tiles/overlay_dark.png | 1 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Tiles/road_0.png | 3 |  | 0 | 0/0 | 0 | 1.6 | 0.0 |  |  |
| Tiles/road_1.png | 3 |  | 0 | 0/0 | 0 | 0.8 | 0.0 |  |  |
| Tiles/road_line.png | 5 |  | 0 | 0/0 | 0 | 0.8 | 0.0 |  |  |
| Tiles/sidewalk_0.png | 4 |  | 0 | 0/0 | 0 | 0.4 | 0.0 |  |  |
| Tiles/sidewalk_1.png | 4 |  | 0 | 0/0 | 0 | 0.4 | 0.0 |  |  |
| Tiles/wall_top.png | 3 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| Tiles/weeds.png | 3 |  | 0 | 0/0 | 0 | 7.1 | 0.0 |  |  |
| Title/title_bg.png | 30 |  | 2 | 8/60 | 1 | 0.1 | 0.0 | moon, night, stone | 一枚絵：明るい星の十字形・月の欠けの先は模様。光の向きは、月（光源）・星・街灯の光のたまりが入るので系統の重心では判断できない |
| Title/title_car_head.png | 2 |  | 0 | 0/0 | 0 | 33.3 | 0.0 |  | 車の光は 3 ドットの光の点（ノイズではない） |
| Title/title_car_tail.png | 2 |  | 0 | 0/0 | 0 | 33.3 | 0.0 |  | 車の光は 3 ドットの光の点（ノイズではない） |
| Title/title_logo.png | 3 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  |  |
| UI/prompt.png | 2 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  | アイコンの中の絵（ランタン・虫めがね・しおり）は 1 ドットの線の絵で、陰影の帯ではない |
| UI/ui_cursor.png | 2 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  | アイコンの中の絵（ランタン・虫めがね・しおり）は 1 ドットの線の絵で、陰影の帯ではない |
| UI/ui_icon_lantern.png | 5 |  | 0 | 2/7 | 0 | 0.8 | 0.0 |  | アイコンの中の絵（ランタン・虫めがね・しおり）は 1 ドットの線の絵で、陰影の帯ではない |
| UI/ui_icon_look.png | 3 |  | 0 | 1/3 | 0 | 0.0 | 0.0 |  | アイコンの中の絵（ランタン・虫めがね・しおり）は 1 ドットの線の絵で、陰影の帯ではない |
| UI/ui_icon_talk.png | 3 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  | アイコンの中の絵（ランタン・虫めがね・しおり）は 1 ドットの線の絵で、陰影の帯ではない |
| UI/ui_name_tab.png | 2 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  | アイコンの中の絵（ランタン・虫めがね・しおり）は 1 ドットの線の絵で、陰影の帯ではない |
| UI/ui_next_0.png | 1 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  | アイコンの中の絵（ランタン・虫めがね・しおり）は 1 ドットの線の絵で、陰影の帯ではない |
| UI/ui_next_1.png | 1 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  | アイコンの中の絵（ランタン・虫めがね・しおり）は 1 ドットの線の絵で、陰影の帯ではない |
| UI/ui_window.png | 2 |  | 0 | 0/0 | 0 | 0.0 | 0.0 |  | アイコンの中の絵（ランタン・虫めがね・しおり）は 1 ドットの線の絵で、陰影の帯ではない |
| UI/ui_wordbook.png | 5 |  | 0 | 1/7 | 0 | 0.0 | 0.0 |  | アイコンの中の絵（ランタン・虫めがね・しおり）は 1 ドットの線の絵で、陰影の帯ではない |
