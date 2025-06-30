<?php
error_reporting(0);

// Flag setup
$flag = file_get_contents('/flag');
putenv("FLAG=".$flag);

// Moodle 4.4.1 calculated question type constants and functions
// Original source: https://git.moodle.org/gw?p=moodle.git;a=blob;f=question/type/calculated/questiontype.php
const PLACEHOLDER_REGEX_PART = '[[:alpha:]][^>} <`{"\']*';
const PLACEHOLDER_REGEX = '~\{(' . PLACEHOLDER_REGEX_PART . ')\}~';

$error = null;
$result = null;
$isCorrect = false;

// from https://git.moodle.org/gw?p=moodle.git;a=blob;f=question/type/calculated/questiontype.php;h=7bd48f61120199b8b7987acd6b6b319201ce891b;hb=db07c09afc52f67a7fa3dc41ba1707ed7f99b58a
function check_formula($formula) {
    foreach (['//', '/*', '#', '<?', '?>'] as $commentstart) {
        if (strpos($formula, $commentstart) !== false) {
            return '허용되지 않는 문자가 포함되어 있습니다';
        }
    }
    
    $formula = preg_replace(PLACEHOLDER_REGEX, '1.0', $formula);
    $formula = strtolower(str_replace(' ', '', $formula));
    
    $safeoperatorchar = '-+/*%>:^\~<?=&|!';
    $operatorornumber = "[{$safeoperatorchar}.0-9eE]";
    
    while (preg_match("~(^|[{$safeoperatorchar},(])([a-z0-9_]*)" .
             "\\(({$operatorornumber}+(,{$operatorornumber}+((,{$operatorornumber}+)+)?)?)?\\)~",
             $formula, $regs)) {
        switch ($regs[2]) {
            case '':
                if ((isset($regs[4]) && $regs[4]) || strlen($regs[3]) == 0) {
                    return '수식 문법이 올바르지 않습니다: '.$regs[0];
                }
                break;
    
            case 'pi':
                if (array_key_exists(3, $regs)) {
                    return $regs[2].' 함수는 인수가 필요하지 않습니다';
                }
                break;

            case 'abs': case 'ceil':
            case 'decbin': case 'decoct': case 'deg2rad':
            case 'exp': case 'floor':
            case 'octdec': case 'rad2deg':
    
            case 'round':
                if (!empty($regs[5]) || empty($regs[3])) {
                    return $regs[2].' 함수는 1개 또는 2개의 인수가 필요합니다';
                }
                break;
    
            default:
                return $regs[2].' 함수는 지원되지 않습니다';
        }
    
        if ($regs[1]) {
            $formula = str_replace($regs[0], $regs[1] . '1.0', $formula);
        } else {
            $formula = preg_replace('~^' . preg_quote($regs[2], '~') . '\([^)]*\)~', '1.0', $formula);
        }
    }
                 
    if (preg_match("~[^{$safeoperatorchar}.0-9eE]+~", $formula, $regs)) {
        return '허용되지 않는 문자입니다: '.$regs[0];
    } else {
        return false;
    }
}

function calculate($formula) {
    global $error;
    $error = check_formula($formula);
    if ($error) {
        return null;
    } else {
        // Variable variables are not allowed - CVE-2024-43425 patch attempt
        $formula = str_replace('{', '(', $formula);
        $formula = str_replace('}', ')', $formula);
        
        return eval('return ' . $formula . ';');
    }
}

// Process calculation
if (isset($_GET['f']) && $_GET['f'] !== '') {
    $formula = $_GET['f'];
    $result = calculate($formula);
    
    // Check if it matches target (for the game aspect)
    $target = 42;
    if (is_numeric($result) && abs($result - $target) < 0.001) {
        $isCorrect = true;
    }
}
?>

<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Number Master - 계산 게임</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        'game-blue': '#1e40af',
                        'game-purple': '#7c3aed',
                    }
                }
            }
        }
    </script>
</head>
<body class="bg-gradient-to-br from-blue-50 to-purple-100 min-h-screen">
    <!-- Header -->
    <div class="bg-white shadow-lg">
        <div class="max-w-6xl mx-auto px-4 py-4">
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-3">
                    <div class="w-10 h-10 bg-gradient-to-r from-game-blue to-game-purple rounded-full flex items-center justify-center">
                        <span class="text-white font-bold text-lg">🧮</span>
                    </div>
                    <div>
                        <h1 class="text-2xl font-bold bg-gradient-to-r from-game-blue to-game-purple bg-clip-text text-transparent">
                            Number Master
                        </h1>
                        <p class="text-sm text-gray-600">수학 함수 계산 게임</p>
                    </div>
                </div>
                <div class="text-right">
                    <div class="text-sm text-gray-500">Level 1</div>
                    <div class="text-lg font-semibold text-game-blue">Score: <?php echo $isCorrect ? 100 : 0; ?></div>
                </div>
            </div>
        </div>
    </div>

    <div class="max-w-4xl mx-auto px-4 py-8">
        <!-- Game Instructions -->
        <div class="bg-white rounded-xl shadow-lg p-6 mb-8">
            <h2 class="text-xl font-bold text-gray-800 mb-4">🎯 게임 규칙</h2>
            <div class="grid md:grid-cols-2 gap-4">
                <div class="bg-blue-50 p-4 rounded-lg">
                    <h3 class="font-semibold text-game-blue mb-2">목표</h3>
                    <p class="text-sm text-gray-700">수학 함수를 사용해서 목표 숫자 42를 만들어보세요!</p>
                </div>
                <div class="bg-purple-50 p-4 rounded-lg">
                    <h3 class="font-semibold text-game-purple mb-2">사용 가능한 함수</h3>
                    <p class="text-sm text-gray-700">abs, ceil, floor, round, exp, decbin, decoct, deg2rad, octdec, rad2deg, pi</p>
                </div>
            </div>
        </div>

        <!-- Game Area -->
        <div class="grid md:grid-cols-2 gap-8">
            <!-- Challenge Card -->
            <div class="bg-white rounded-xl shadow-lg p-6">
                <h3 class="text-lg font-bold text-gray-800 mb-4">📊 현재 도전</h3>
                <div class="bg-gradient-to-r from-game-blue to-game-purple p-6 rounded-lg text-white text-center mb-4">
                    <div class="text-sm opacity-90 mb-2">목표 숫자</div>
                    <div class="text-4xl font-bold">42</div>
                </div>
                
                <div class="mb-4">
                    <label class="block text-sm font-medium text-gray-700 mb-2">사용 가능한 숫자</label>
                    <div class="flex flex-wrap gap-2">
                        <span class="px-3 py-1 bg-blue-100 text-game-blue rounded-full text-sm font-medium">1</span>
                        <span class="px-3 py-1 bg-blue-100 text-game-blue rounded-full text-sm font-medium">2</span>
                        <span class="px-3 py-1 bg-blue-100 text-game-blue rounded-full text-sm font-medium">3</span>
                        <span class="px-3 py-1 bg-blue-100 text-game-blue rounded-full text-sm font-medium">7</span>
                        <span class="px-3 py-1 bg-blue-100 text-game-blue rounded-full text-sm font-medium">10</span>
                        <span class="px-3 py-1 bg-blue-100 text-game-blue rounded-full text-sm font-medium">100</span>
                        <span class="px-3 py-1 bg-blue-100 text-game-blue rounded-full text-sm font-medium">1000</span>
                    </div>
                </div>

                <div class="space-y-3">
                    <div class="flex items-center space-x-2 text-sm">
                        <span class="w-2 h-2 bg-green-500 rounded-full"></span>
                        <span class="text-gray-600">exp() 함수로 큰 수를 만들 수 있어요</span>
                    </div>
                    <div class="flex items-center space-x-2 text-sm">
                        <span class="w-2 h-2 bg-yellow-500 rounded-full"></span>
                        <span class="text-gray-600">여러 함수를 조합해보세요</span>
                    </div>
                    <div class="flex items-center space-x-2 text-sm">
                        <span class="w-2 h-2 bg-purple-500 rounded-full"></span>
                        <span class="text-gray-600">창의적인 수식을 만들어보세요</span>
                    </div>
                </div>
            </div>

            <!-- Calculator Interface -->
            <div class="bg-white rounded-xl shadow-lg p-6">
                <h3 class="text-lg font-bold text-gray-800 mb-4">🧮 계산기</h3>
                
                <form method="GET" action="game.php" class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">수식 입력</label>
                        <input 
                            type="text" 
                            name="f" 
                            id="formula"
                            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-game-blue focus:border-transparent text-lg font-mono"
                            placeholder="예: abs(-42) 또는 exp(3) + 22"
                            value="<?php echo isset($_GET['f']) ? htmlspecialchars($_GET['f']) : ''; ?>"
                        />
                    </div>
                    
                    <!-- Function Buttons -->
                    <div class="grid grid-cols-5 gap-2">
                        <button type="button" onclick="addFunction('abs')" class="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded text-sm font-medium transition-colors">abs</button>
                        <button type="button" onclick="addFunction('ceil')" class="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded text-sm font-medium transition-colors">ceil</button>
                        <button type="button" onclick="addFunction('floor')" class="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded text-sm font-medium transition-colors">floor</button>
                        <button type="button" onclick="addFunction('round')" class="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded text-sm font-medium transition-colors">round</button>
                        <button type="button" onclick="addFunction('exp')" class="px-3 py-2 bg-purple-100 hover:bg-purple-200 text-game-purple rounded text-sm font-medium transition-colors">exp</button>
                        <button type="button" onclick="addFunction('decbin')" class="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded text-sm font-medium transition-colors">decbin</button>
                        <button type="button" onclick="addFunction('decoct')" class="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded text-sm font-medium transition-colors">decoct</button>
                        <button type="button" onclick="addFunction('deg2rad')" class="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded text-sm font-medium transition-colors">deg2rad</button>
                        <button type="button" onclick="addFunction('octdec')" class="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded text-sm font-medium transition-colors">octdec</button>
                        <button type="button" onclick="addFunction('rad2deg')" class="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded text-sm font-medium transition-colors">rad2deg</button>
                    </div>

                    <!-- Number and Operator Buttons -->
                    <div class="grid grid-cols-6 gap-2">
                        <button type="button" onclick="addToFormula('1')" class="px-3 py-2 bg-blue-100 hover:bg-blue-200 text-game-blue rounded font-medium transition-colors">1</button>
                        <button type="button" onclick="addToFormula('2')" class="px-3 py-2 bg-blue-100 hover:bg-blue-200 text-game-blue rounded font-medium transition-colors">2</button>
                        <button type="button" onclick="addToFormula('3')" class="px-3 py-2 bg-blue-100 hover:bg-blue-200 text-game-blue rounded font-medium transition-colors">3</button>
                        <button type="button" onclick="addToFormula('7')" class="px-3 py-2 bg-blue-100 hover:bg-blue-200 text-game-blue rounded font-medium transition-colors">7</button>
                        <button type="button" onclick="addToFormula('10')" class="px-3 py-2 bg-blue-100 hover:bg-blue-200 text-game-blue rounded font-medium transition-colors">10</button>
                        <button type="button" onclick="addToFormula('100')" class="px-3 py-2 bg-blue-100 hover:bg-blue-200 text-game-blue rounded font-medium transition-colors">100</button>
                        <button type="button" onclick="addToFormula('+')" class="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded font-medium transition-colors">+</button>
                        <button type="button" onclick="addToFormula('-')" class="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded font-medium transition-colors">-</button>
                        <button type="button" onclick="addToFormula('*')" class="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded font-medium transition-colors">×</button>
                        <button type="button" onclick="addToFormula('/')" class="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded font-medium transition-colors">÷</button>
                        <button type="button" onclick="addToFormula('(')" class="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded font-medium transition-colors">(</button>
                        <button type="button" onclick="addToFormula(')')" class="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded font-medium transition-colors">)</button>
                        <button type="button" onclick="addToFormula('.')" class="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded font-medium transition-colors">.</button>
                        <button type="button" onclick="addToFormula('^')" class="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded font-medium transition-colors">^</button>
                        <button type="button" onclick="addToFormula('1000')" class="px-3 py-2 bg-blue-100 hover:bg-blue-200 text-game-blue rounded font-medium transition-colors">1000</button>
                        <button type="button" onclick="clearFormula()" class="px-3 py-2 bg-red-100 hover:bg-red-200 text-red-600 rounded font-medium transition-colors">Clear</button>
                    </div>

                    <button 
                        type="submit" 
                        class="w-full bg-gradient-to-r from-game-blue to-game-purple text-white py-3 rounded-lg font-semibold hover:shadow-lg transition-all duration-200 transform hover:scale-105"
                    >
                        🚀 계산하기!
                    </button>
                </form>

                <!-- Result Display -->
                <?php if(isset($result) && !$error): ?>
                <div class="mt-6 p-4 <?php echo $isCorrect ? 'bg-green-50 border border-green-200' : 'bg-blue-50 border border-blue-200'; ?> rounded-lg">
                    <div class="flex items-center space-x-2">
                        <?php if($isCorrect): ?>
                            <span class="text-green-500">🎉</span>
                            <span class="font-semibold text-green-800">정답입니다! 42를 만들었어요!</span>
                        <?php else: ?>
                            <span class="text-blue-500">📊</span>
                            <div class="font-semibold text-blue-800">
                                결과: 
                                <pre class="mt-2 text-sm bg-gray-100 p-2 rounded overflow-auto max-h-96"><?php echo htmlspecialchars($result); ?></pre>
                            </div>
                        <?php endif; ?>
                    </div>
                    
                    <?php if($isCorrect): ?>
                    <div class="mt-4 p-3 bg-green-100 rounded-lg">
                        <div class="text-sm text-green-700">
                            <p class="font-semibold">🏆 레벨 클리어!</p>
                            <p>축하합니다! 다음 레벨에 도전해보세요.</p>
                        </div>
                    </div>
                    <?php endif; ?>
                </div>
                <?php elseif(isset($error)): ?>
                <div class="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                    <div class="flex items-center space-x-2">
                        <span class="text-red-500">❌</span>
                        <span class="font-semibold text-red-800"><?php echo htmlspecialchars($error); ?></span>
                    </div>
                </div>
                <?php endif; ?>
            </div>
        </div>

        <!-- Leaderboard -->
        <div class="mt-8 bg-white rounded-xl shadow-lg p-6">
            <h3 class="text-lg font-bold text-gray-800 mb-4">🏆 명예의 전당</h3>
            <div class="grid md:grid-cols-3 gap-4">
                <div class="bg-gradient-to-r from-yellow-400 to-yellow-500 p-4 rounded-lg text-white">
                    <div class="text-center">
                        <div class="text-2xl mb-2">🥇</div>
                        <div class="font-bold">MathWiz</div>
                        <div class="text-sm opacity-90">Level 42 Master</div>
                    </div>
                </div>
                <div class="bg-gradient-to-r from-gray-400 to-gray-500 p-4 rounded-lg text-white">
                    <div class="text-center">
                        <div class="text-2xl mb-2">🥈</div>
                        <div class="font-bold">CalcPro</div>
                        <div class="text-sm opacity-90">Level 35</div>
                    </div>
                </div>
                <div class="bg-gradient-to-r from-orange-400 to-orange-500 p-4 rounded-lg text-white">
                    <div class="text-center">
                        <div class="text-2xl mb-2">🥉</div>
                        <div class="font-bold">NumberFan</div>
                        <div class="text-sm opacity-90">Level 28</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Footer -->
    <footer class="bg-gray-800 text-white py-8 mt-12">
        <div class="max-w-4xl mx-auto px-4 text-center">
            <div class="mb-4">
                <span class="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">Number Master</span>
            </div>
            <p class="text-gray-400">수학 함수 계산 게임</p>
            <p class="text-sm text-gray-500 mt-2">재미있는 수학 학습을 위해</p>
        </div>
    </footer>

    <script>
        function addFunction(func) {
            const formula = document.getElementById('formula');
            formula.value += func + '(';
            formula.focus();
        }

        function addToFormula(value) {
            const formula = document.getElementById('formula');
            formula.value += value;
            formula.focus();
        }

        function clearFormula() {
            document.getElementById('formula').value = '';
            document.getElementById('formula').focus();
        }
    </script>
</body>
</html>
