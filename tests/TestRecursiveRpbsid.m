classdef TestRecursiveRpbsid < matlab.unittest.TestCase
    properties
        RepoRoot
    end

    methods (TestMethodSetup)
        function addToolboxToPath(testCase)
            testCase.RepoRoot = fileparts(fileparts(mfilename('fullpath')));
            addpath(testCase.RepoRoot);
        end
    end

    methods (TestMethodTeardown)
        function removeToolboxFromPath(testCase)
            rmpath(testCase.RepoRoot);
        end
    end

    methods (Test)
        function rpbsidRunsAndReturnsFiniteOutputs(testCase)
            [u, y, sys] = testutils.makeSisoData('N', 260, 'seed', 70, 'noiseStd', 0.03);

            f = 5;
            p = 10;
            n = 1;

            % Request extra outputs to cover more internal branches
            [A, B, C, D, K, err, eigA, regA] = rpbsid(u, y, f, p, n);

            testCase.verifySize(A, [n n]);
            testCase.verifySize(B, [n 1]);
            testCase.verifySize(C, [1 n]);
            testCase.verifySize(D, [1 1]);
            testCase.verifySize(K, [n 1]);

            testCase.verifyTrue(all(isfinite(A(:))));
            testCase.verifyTrue(all(isfinite(B(:))));
            testCase.verifyTrue(all(isfinite(C(:))));
            testCase.verifyTrue(all(isfinite(D(:))));
            testCase.verifyTrue(all(isfinite(K(:))));

            % err, eigA, regA should be finite and have expected lengths
            testCase.verifyTrue(all(isfinite(err(:))));
            testCase.verifyTrue(all(isfinite(eigA(:))));
            testCase.verifyTrue(all(isfinite(regA(:))));

            testCase.verifyEqual(size(eigA, 1), n);
            testCase.verifyEqual(size(eigA, 2), sys.N);

            % regA is returned as a vector over time in this implementation
            testCase.verifyGreaterThanOrEqual(numel(regA), 1);
        end
    end
end