using BlueNight.Dialogue;
using BlueNight.Shadows;
using UnityEngine;

namespace BlueNight.Audio
{
    /// <summary>
    /// 逃げた影を追う場面の音（仕様書 8.3）。
    /// - 影に近づくと、町の曲から「影を追う」曲へクロスフェード（最初は土台の層だけ）。
    /// - もっと近づくと太鼓、追いつめる直前には弦の層が加わる。離れると層が抜け、町の曲へ戻る。
    /// - 捕まえたらスティンガーを鳴らし、「影の言葉」へクロスフェード。会話が終わったら町の曲へ。
    /// - 影の近くでは「影の気配」の音がかすかに鳴り、びくっとしたときは「すっと逃げる」音。
    /// </summary>
    public class ChaseMusic : MonoBehaviour
    {
        [SerializeField] RunawayShadow shadow;
        [SerializeField] Transform player;
        [SerializeField] string fieldTrack = "ch1_shopping_street";
        [SerializeField] string chaseTrack = "shadow_chase";
        [SerializeField] string wordsTrack = "shadow_words";
        [SerializeField] string stinger = "stinger_shadow_capture";
        [SerializeField, Tooltip("この距離（マス）より近づくと、追う曲になる")] float chaseDistance = 9f;
        [SerializeField] float drumsDistance = 5f;
        [SerializeField] float stringsDistance = 2.6f;
        [SerializeField] float presenceDistance = 6f;

        AudioSource presence;
        bool captured;
        bool wordsPlaying;

        public void Configure(RunawayShadow runawayShadow, Transform playerTransform, string field)
        {
            shadow = runawayShadow;
            player = playerTransform;
            fieldTrack = field;
        }

        void Start()
        {
            if (shadow == null)
                return;
            shadow.Captured += OnCaptured;
            shadow.Escaped += OnEscaped;
            shadow.Surprised += () => SoundEffects.Play("shadow_escape", 0.8f);
            presence = SoundEffects.CreateLoop("shadow_presence", shadow.transform);
        }

        void OnCaptured()
        {
            captured = true;
            wordsPlaying = true;
            SoundEffects.Play("shadow_capture");
            var music = MusicDirector.Instance;
            if (music == null)
                return;
            music.PlayStinger(stinger);
            music.CrossFade(wordsTrack, 3.5f);
        }

        void OnEscaped()
        {
            captured = true;
            wordsPlaying = false;
            MusicDirector.Instance?.CrossFade(fieldTrack, 3f);
        }

        void Update()
        {
            var music = MusicDirector.Instance;
            if (shadow == null || player == null || music == null)
                return;

            float distance = Vector2.Distance(shadow.transform.position, player.position);

            if (presence != null)
            {
                float near = shadow.IsFleeing ? Mathf.Clamp01(1f - distance / presenceDistance) : 0f;
                presence.volume = Mathf.MoveTowards(presence.volume, SoundEffects.LoopVolume(near * 0.8f), Time.unscaledDeltaTime);
            }

            if (captured)
            {
                // 影の言葉を聞き終えたら、町の曲へ
                if (wordsPlaying && !shadow.IsSpeaking && !DialogueRunner.IsBusy)
                {
                    wordsPlaying = false;
                    music.CrossFade(fieldTrack, 3f);
                }
                return;
            }

            if (!shadow.IsFleeing || !shadow.gameObject.activeInHierarchy)
                return;

            if (distance < chaseDistance)
            {
                if (music.CurrentTrack != chaseTrack)
                    music.CrossFade(chaseTrack, 2f, "base");
                music.SetLayer("drums", distance < drumsDistance, 1.5f);
                music.SetLayer("strings", distance < stringsDistance, 1f);
            }
            else if (distance > chaseDistance + 2f && music.CurrentTrack == chaseTrack)
            {
                music.CrossFade(fieldTrack, 2.5f);
            }
        }
    }
}
