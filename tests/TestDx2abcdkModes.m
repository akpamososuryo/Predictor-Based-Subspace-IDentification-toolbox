classdef TestDx2abcdkModes < matlab.unittest.TestCase
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
        function baselineAndStable1BranchesRun(testCase)
            d0 = testutils.makeDx2abcdkData('stable', 'seed', 30);
            [A, B, C, D, K] = dx2abcdk(d0.x, d0.u, d0.y, d0.f, d0.p);

            testCase.verifySize(A, [2 2]);
            testCase.verifySize(B, [2 1]);
            testCase.verifySize(C, [1 2]);
            testCase.verifySize(D, [1 1]);
            testCase.verifySize(K, [2 1]);

            testCase.verifyTrue(all(isfinite(A(:))));
            testCase.verifyTrue(all(isfinite(B(:))));
            testCase.verifyTrue(all(isfinite(C(:))));
            testCase.verifyTrue(all(isfinite(D(:))));
            testCase.verifyTrue(all(isfinite(K(:))));

            d1 = testutils.makeDx2abcdkData('unstable', 'seed', 31);
            [As, Bs, Cs, Ds] = dx2abcdk(d1.x, d1.u, d1.y, d1.f, d1.p, 'stable1');

            testCase.verifySize(As, [2 2]);
            testCase.verifySize(Bs, [2 1]);
            testCase.verifySize(Cs, [1 2]);
            testCase.verifySize(Ds, [1 1]);
            testCase.verifyLessThan(max(abs(eig(As))), 1.0);
        end
    end
end
